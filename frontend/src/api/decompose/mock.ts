// @ts-nocheck
// ============================================================
// 信息拆解 · mock 层
// 与真实后端 API 同形状（见 docs/拆解契约.md 第 6/8 章）
// 用定时器模拟 SSE 事件流，localStorage 持久化任务
// ============================================================

const TASKS_KEY = 'decompose_mock_tasks_v1'
const subscribers = new Map() // taskId -> handlers

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const now = () => new Date().toISOString()
let seq = 0
const uid = (prefix) => { seq += 1; return `${prefix}-${Date.now().toString().slice(-6)}-${seq}` }

function loadTasks() {
  try { return JSON.parse(localStorage.getItem(TASKS_KEY) || '[]') } catch (e) { return [] }
}
function saveTasks(tasks) {
  try { localStorage.setItem(TASKS_KEY, JSON.stringify(tasks)) } catch (e) { /* 忽略 */ }
}
function findTask(id) {
  const task = loadTasks().find((t) => t.id === id)
  if (!task) throw new Error(`任务不存在: ${id}`)
  return task
}
function persist(task) {
  const tasks = loadTasks().map((t) => (t.id === task.id ? task : t))
  saveTasks(tasks)
}
function emit(taskId, type, data) {
  const handlers = subscribers.get(taskId)
  if (handlers && handlers[type]) handlers[type]({ type, task_id: taskId, ...data })
}

// ---------------- 契约生成（规则式 mock，保证结果真实可读） ----------------

function splitFacts(content) {
  return content
    .split(/[。；;！!？?\n]/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 4)
}

function kindOf(text) {
  if (/要求|需|必须|具备|熟练|精通|优先/.test(text)) return 'requirement'
  if (/\$|€|¥|元|价格|售价|单价|折扣/.test(text)) return 'pricing'
  if (/https?:\/\//.test(text)) return 'link'
  if (/年|个月|天|周/.test(text)) return 'duration'
  if (/评分|评论|评价|退货|差评/.test(text)) return 'reputation'
  return 'info'
}

function buildS0(source) {
  const content = source.content || ''
  const sentenceCount = splitFacts(content).length
  return {
    contract_name: 'S0',
    version: 1,
    status: 'needs_human',
    created_at: now(),
    facts: [
      {
        id: 'F-000',
        kind: 'source_meta',
        content: `材料共 ${content.length} 字，约 ${sentenceCount} 句，来源类型 text`,
        anchor: '整篇',
        confidence: 'C3'
      }
    ],
    inferences: [
      {
        id: 'I-001',
        type: 'brief',
        content: `拆解目标：${source.target || '提取关键信息并归纳结论'}`,
        evidence: ['F-000'],
        confidence: 'C2'
      }
    ],
    meta: {
      source_type: 'text',
      word_count: content.length,
      target_question: source.target || '提取关键信息',
      errors: [],
      data_gaps: []
    }
  }
}

function buildS1(source, s0) {
  const sentences = splitFacts(source.content)
  const facts = sentences.map((text, index) => ({
    id: `F-${String(index + 1).padStart(3, '0')}`,
    kind: kindOf(text),
    content: text,
    anchor: `第 ${index + 1} 句`,
    confidence: 'C3'
  }))
  const gapCount = facts.length === 0 ? 1 : 0
  return {
    contract_name: 'S1',
    version: 1,
    status: 'needs_human',
    created_at: now(),
    facts,
    inferences: [
      {
        id: 'I-010',
        type: 'cluster',
        content: `共拆出 ${facts.length} 条事实，类型分布：${groupKinds(facts)}`,
        evidence: facts.slice(0, 3).map((f) => f.id),
        confidence: 'C3'
      }
    ],
    meta: {
      source_type: 'text',
      word_count: source.content.length,
      target_question: s0.meta.target_question,
      errors: [],
      data_gaps: gapCount > 0 ? ['材料过短，未拆出有效事实，可补充更完整的材料重跑'] : []
    }
  }
}

function groupKinds(facts) {
  const counts = {}
  facts.forEach((f) => { counts[f.kind] = (counts[f.kind] || 0) + 1 })
  return Object.entries(counts).map(([k, v]) => `${k}×${v}`).join(' / ')
}

function buildS2(source, s1) {
  const facts = s1.facts || []
  const fallbackFact = facts[0]
  const pick = (kind) => facts.find((f) => f.kind === kind)
  const evidenceOf = (ids) => {
    const ok = ids.filter(Boolean)
    return ok.length ? ok : fallbackFact ? [fallbackFact.id] : []
  }
  const requirement = pick('requirement') || fallbackFact
  const pricing = pick('pricing')
  const reputation = pick('reputation')
  const info = pick('info') || requirement
  const inferences = []

  // usp 核心卖点 / 关键要求
  if (requirement) {
    inferences.push({
      id: 'I-101', type: 'usp',
      content: `核心卖点/关键要求：${shorten(requirement.content, 40)}。这是材料最突出的抓手，应作为后续调研与验证的主线。`,
      evidence: evidenceOf([requirement.id]), confidence: 'C3'
    })
  }

  // pricing 定价与成本
  if (pricing) {
    inferences.push({
      id: 'I-102', type: 'pricing',
      content: `定价/成本：${shorten(pricing.content, 40)}。可作为定价区间或成本对比锚点，建议与同类产品横向对比后确认合理性。`,
      evidence: evidenceOf([pricing.id]), confidence: 'C3'
    })
  } else {
    inferences.push({
      id: 'I-102', type: 'pricing',
      content: '定价/成本：材料未提及，属于数据缺口，建议补充价格、成本或预算信息后再评估。',
      evidence: evidenceOf([]), confidence: 'C1'
    })
  }

  // risk 风险与短板
  if (reputation) {
    inferences.push({
      id: 'I-103', type: 'risk',
      content: `风险与短板：${shorten(reputation.content, 40)}。负面信号需要重点核实，必要时补充差评/退货来源交叉验证。`,
      evidence: evidenceOf([reputation.id]), confidence: 'C2'
    })
  } else {
    inferences.push({
      id: 'I-103', type: 'risk',
      content: '风险与短板：材料未给出明显负面信号，但仍需对时效性、合规性等隐性风险保持警惕。',
      evidence: evidenceOf([]), confidence: 'C1'
    })
  }

  // opportunity 机会与空间
  if (info) {
    inferences.push({
      id: 'I-104', type: 'opportunity',
      content: `机会与空间：${shorten(info.content, 40)}。可围绕这一信息点展开进一步调研，评估扩展或优化的空间。`,
      evidence: evidenceOf([info.id]), confidence: 'C2'
    })
  }

  // audience 目标人群 / 适用场景
  const audienceFact = facts.find((f) => /面向|适合|针对|人群|用户|客户|玩家|学生|职场|宝妈|老人|儿童/.test(f.content))
  if (audienceFact) {
    inferences.push({
      id: 'I-105', type: 'audience',
      content: `目标人群/适用场景：${shorten(audienceFact.content, 40)}。可进一步明确人群画像与核心场景，指导卖点排序。`,
      evidence: evidenceOf([audienceFact.id]), confidence: 'C2'
    })
  } else {
    inferences.push({
      id: 'I-105', type: 'audience',
      content: '目标人群/适用场景：材料未明确，建议补充目标用户画像或使用场景信息。',
      evidence: evidenceOf([]), confidence: 'C1'
    })
  }

  // action 行动建议
  inferences.push({
    id: 'I-106', type: 'action',
    content: requirement
      ? `行动建议：优先验证 C1/C2 低置信度结论（补来源、补数据），再围绕「${shorten(requirement.content, 20)}」制定下一步方案并排期。`
      : '行动建议：优先补充材料缺口，再围绕核心卖点制定下一步方案并排期。',
    evidence: evidenceOf(requirement ? [requirement.id] : []), confidence: 'C2'
  })

  return {
    contract_name: 'S2',
    version: 1,
    status: 'needs_human',
    created_at: now(),
    facts: [],
    inferences,
    meta: {
      source_type: 'text',
      word_count: source.content.length,
      target_question: s1.meta.target_question,
      errors: [],
      data_gaps: s1.meta.data_gaps || []
    }
  }
}

function shorten(text, max) { return text.length > max ? text.slice(0, max) + '…' : text }

const S2_TITLES = {
  usp: '核心卖点 / 关键要求',
  pricing: '定价与成本',
  risk: '风险与短板',
  opportunity: '机会与空间',
  audience: '目标人群 / 适用场景',
  action: '行动建议'
}

function buildS3(task, s2) {
  const byType = {}
  ;(s2.inferences || []).forEach((i) => {
    ;(byType[i.type] = byType[i.type] || []).push(i)
  })
  const sections = []
  Object.entries(S2_TITLES).forEach(([key, title]) => {
    const group = byType[key]
    if (!group) return
    const evidence = []
    const contents = []
    group.forEach((i) => {
      contents.push(i.content || '')
      ;(i.evidence || []).forEach((e) => { if (!evidence.includes(e)) evidence.push(e) })
    })
    sections.push({ type: key, title, content: contents.join('；'), evidence: evidence.slice(0, 5) })
  })
  const gaps = (s2.meta && s2.meta.data_gaps) || []
  const summaryLines = [
    `材料共 ${task.source.content.length} 字，拆出 ${(task.contracts.S1?.facts || []).length} 条事实、${(s2.inferences || []).length} 条结论。`,
    '核心结论：' + ((s2.inferences || []).slice(0, 2).map((i) => i.content).join('；') || '暂无结论。')
  ]
  if (gaps.length) summaryLines.push('主要缺口：' + gaps.join('；'))
  return {
    contract_name: 'S3',
    version: task.version,
    status: 'auto_ok',
    created_at: now(),
    facts: [],
    inferences: s2.inferences.map((i) => ({ ...i })),
    meta: {
      source_type: 'text',
      word_count: task.source.content.length,
      target_question: s2.meta.target_question,
      errors: [],
      data_gaps: gaps,
      exported_at: now(),
      summary: summaryLines.join(' '),
      sections,
      actions: [
        '对 C1/C2 低置信度结论补充来源或数据验证后再引用',
        '按「行动建议」要点落实下一步，并复核风险与定价假设'
      ]
    }
  }
}

// ---------------- 状态机推进（模拟后端编排） ----------------

function createTaskInternal(payload) {
  const id = uid('task')
  const source = {
    content: (payload.content || '').trim(),
    target: (payload.target || '').trim()
  }
  const task = {
    id,
    title: shorten(source.content.split('\n')[0] || '未命名拆解', 30),
    state: 'DRAFT',
    version: 1,
    created_at: now(),
    source,
    contracts: {},
    gates: {
      A: { id: `${id}-A`, name: 'Brief 确认', state: 'pending', decided_at: null, note: '' },
      B: { id: `${id}-B`, name: '事实清单确认', state: 'pending', decided_at: null, note: '' },
      C: { id: `${id}-C`, name: '结论确认', state: 'pending', decided_at: null, note: '' }
    },
    error: null,
    _cancelled: false,
    _handlers: null
  }
  const tasks = loadTasks()
  tasks.unshift(task)
  saveTasks(tasks)
  runFrom(task, 'S0')
  return id
}

async function runFrom(task, from, versionBump = false) {
  task._cancelled = true
  await delay(30) // 让旧流程退出
  task._cancelled = false
  task._handlers = subscribers.get(task.id) || null
  if (versionBump) task.version += 1

  try {
    if (from === 'S0') {
      emit(task.id, 'thinking', { contract: 'S0', message: 'S0 输入解析：识别拆解目标与材料结构' })
      await delay(900)
      if (task._cancelled) return
      const s0 = buildS0(task.source)
      s0.version = task.version
      task.contracts.S0 = s0
      task.state = 'BRIEF_REVIEW'
      task.gates.A.state = 'pending'
      persist(task)
      emit(task.id, 'output', { contract: 'S0', contract_body: s0 })
      emit(task.id, 'gate', { gate: 'A', message: '请确认拆解目标' })
      return
    }

    if (from === 'S1' || !task.contracts.S0) {
      task.state = 'DECOMPOSING'
      persist(task)
      emit(task.id, 'thinking', { contract: 'S1', message: 'S1 事实拆解：逐句拆解并标注原文锚点' })
      await delay(1200)
      if (task._cancelled) return
      const s1 = buildS1(task.source, task.contracts.S0)
      s1.version = task.version
      task.contracts.S1 = s1
      task.state = 'FACTS_REVIEW'
      task.gates.B.state = 'pending'
      persist(task)
      emit(task.id, 'output', { contract: 'S1', contract_body: s1 })
      emit(task.id, 'gate', { gate: 'B', message: '请确认事实清单，可标记错/缺' })
      return
    }

    if (from === 'S2') {
      task.state = 'INSIGHTING'
      persist(task)
      emit(task.id, 'thinking', { contract: 'S2', message: 'S2 洞察生成：基于已确认事实归纳结论' })
      await delay(1200)
      if (task._cancelled) return
      const s2 = buildS2(task.source, task.contracts.S1)
      s2.version = task.version
      task.contracts.S2 = s2
      task.state = 'INSIGHT_REVIEW'
      task.gates.C.state = 'pending'
      persist(task)
      emit(task.id, 'output', { contract: 'S2', contract_body: s2 })
      emit(task.id, 'gate', { gate: 'C', message: '请确认结论' })
      return
    }

    if (from === 'S3') {
      task.state = 'REPORTING'
      persist(task)
      emit(task.id, 'thinking', { contract: 'S3', message: 'S3 报告合成：汇总已确认结论' })
      await delay(700)
      if (task._cancelled) return
      task.contracts.S3 = buildS3(task, task.contracts.S2)
      task.state = 'DONE'
      task._handlers = null
      persist(task)
      emit(task.id, 'output', { contract: 'S3', contract_body: task.contracts.S3 })
      emit(task.id, 'complete', { message: '拆解完成' })
      return
    }
  } catch (e) {
    task.state = 'FAILED'
    task.error = e.message
    task._handlers = null
    persist(task)
    emit(task.id, 'error', { message: e.message })
  }
}

function decideGateInternal(taskId, gateKey, action, note) {
  const task = findTask(taskId)
  const gate = task.gates[gateKey]
  if (!gate || gate.state !== 'pending') throw new Error(`闸门 ${gateKey} 不在待确认状态`)

  if (action === 'regenerate') {
    gate.note = note || ''
    if (gateKey === 'A') {
      delete task.contracts.S0
      delete task.contracts.S1
      delete task.contracts.S2
      delete task.contracts.S3
      runFrom(task, 'S0', true)
    } else if (gateKey === 'B') {
      delete task.contracts.S1
      delete task.contracts.S2
      delete task.contracts.S3
      runFrom(task, 'S1', true)
    } else {
      delete task.contracts.S2
      delete task.contracts.S3
      runFrom(task, 'S2', true)
    }
    return task.id
  }

  gate.state = 'approved'
  gate.decided_at = now()
  gate.note = note || ''
  const current = task.contracts[gateKey === 'A' ? 'S0' : gateKey === 'B' ? 'S1' : 'S2']
  if (current) current.status = 'human_approved'
  if (gateKey === 'A') runFrom(task, 'S1')
  else if (gateKey === 'B') runFrom(task, 'S2')
  else runFrom(task, 'S3')
  return task.id
}

// ---------------- 对外 API（与真实后端同形状） ----------------

export const decomposeMock = {
  async createTask(payload) {
    await delay(120)
    const id = createTaskInternal(payload)
    return findTask(id)
  },

  async listTasks() {
    return loadTasks().map(({ id, title, state, version, created_at, error, gates }) => ({
      id, title, state, version, created_at, error, gates
    }))
  },

  async getTask(id) {
    await delay(100)
    const task = findTask(id)
    const { _cancelled, _handlers, ...detail } = task
    return detail
  },

  async getGates(taskId) {
    const task = findTask(taskId)
    return Object.values(task.gates).map((g) => ({ ...g }))
  },

  async decideGate(gateId, { action, note = '' }) {
    await delay(150)
    const key = gateId.match(/-([ABC])$/)
    if (!key) throw new Error(`无效闸门 ID: ${gateId}`)
    const realTaskId = gateId.slice(0, -2)
    const id = decideGateInternal(realTaskId, key[1], action, note)
    return findTask(id)
  },

  async deleteTask(taskId) {
    await delay(100)
    const tasks = loadTasks().filter((t) => t.id !== taskId)
    saveTasks(tasks)
    subscribers.delete(taskId)
    return { ok: true, id: taskId }
  },

  async rerun(taskId, from) {
    await delay(150)
    const task = findTask(taskId)
    const contract = { S0: 'S0', S1: 'S1', S2: 'S2', S3: 'S3' }[from] || 'S0'
    delete task.contracts[contract]
    if (contract === 'S0') { delete task.contracts.S1; delete task.contracts.S2; delete task.contracts.S3 }
    if (contract === 'S1') { delete task.contracts.S2; delete task.contracts.S3 }
    if (contract === 'S2') { delete task.contracts.S3 }
    task.error = null
    runFrom(task, contract, true)
    return task.id
  },

  async exportTask(taskId) {
    await delay(300)
    const task = findTask(taskId)
    const s3 = task.contracts.S3
    const s2 = task.contracts.S2
    const s1 = task.contracts.S1
    const s3Meta = (s3 && s3.meta) || {}
    const inferences = (s3 && s3.inferences) || (s2 && s2.inferences) || []
    const facts = (s1 && s1.facts) || []
    const sections = s3Meta.sections || []
    const actions = s3Meta.actions || []
    const gaps = s3Meta.data_gaps || (s2 && s2.meta && s2.meta.data_gaps) || []
    const lines = [
      `# 信息拆解报告 · ${task.title}`,
      '',
      `- 任务 ID: ${task.id}  |  版本 v${task.version}  |  完成时间: ${task.created_at}`,
      `- 拆解目标: ${task.source.target || '提取关键信息并归纳结论'}`,
      `- 材料规模: ${task.source.content.length} 字  |  事实 ${facts.length} 条  |  结论 ${inferences.length} 条`,
      '',
      '## 执行摘要',
      '',
      s3Meta.summary || '（无）',
      '',
      '## 结论（按要点）',
      ''
    ]
    if (sections.length) {
      sections.forEach((s) => {
        lines.push(`### ${s.title || s.type}`)
        lines.push('')
        lines.push(s.content || '（无）')
        if (s.evidence && s.evidence.length) {
          lines.push('')
          lines.push(`- 证据: ${s.evidence.join('、')}`)
        }
        lines.push('')
      })
    } else {
      inferences.forEach((i) => {
        lines.push(`- [${i.type}] ${i.content}（置信度 ${i.confidence}，证据 ${i.evidence.join('、') || '无'}）`)
      })
      lines.push('')
    }
    lines.push('## 结论明细', '')
    inferences.forEach((i) => {
      lines.push(`- [${i.type}] ${i.content}（置信度 ${i.confidence}，证据 ${i.evidence.join('、') || '无'}）`)
    })
    lines.push('', '## 事实清单', '')
    facts.forEach((f) => {
      lines.push(`- ${f.id}（${f.kind}）${f.content}  [锚点: ${f.anchor}]`)
    })
    lines.push('', '## 数据缺口', '')
    if (gaps.length) gaps.forEach((g) => lines.push(`- ${g}`))
    else lines.push('- 无')
    lines.push('', '## 闸门确认记录', '')
    const decided = Object.values(task.gates).filter((g) => g.state === 'approved' || g.note)
    if (decided.length) {
      decided.forEach((g) => lines.push(`- 闸门 ${g.name}：${g.note ? `意见「${g.note}」` : '确认'} @ ${g.decided_at || ''}`))
    } else {
      lines.push('- 无')
    }
    lines.push('', '## 下一步建议', '')
    if (actions.length) actions.forEach((a) => lines.push(`- ${a}`))
    else lines.push('- 无')
    return { markdown: lines.join('\n') }
  },

  subscribeEvents(taskId, handlers) {
    subscribers.set(taskId, handlers)
    return () => { subscribers.delete(taskId) }
  }
}
