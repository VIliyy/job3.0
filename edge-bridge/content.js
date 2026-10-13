// 小林工具箱 · BOSS 海投记录助手 - 页面内容脚本
// 在 BOSS 直聘职位页注入浮层面板：提取岗位信息 -> 记录到本地工具箱 -> 人工复制打招呼语发送
// 安全边界：本脚本绝不自动点击发送/聊天，只做「提取 + 记录 + 起草」

(function () {
  'use strict';
  if (window.__XL_BRIDGE_LOADED__) { return; }
  window.__XL_BRIDGE_LOADED__ = true;

  var HOST_ID = 'xlb-boss-bridge-root';

  function bridge(type, payload) {
    return new Promise(function (resolve) {
      var msg = { type: type, payload: payload };
      chrome.runtime.sendMessage(msg, function (resp) {
        if (chrome.runtime.lastError) {
          resolve({ ok: false, error: chrome.runtime.lastError.message });
          return;
        }
        resolve(resp || { ok: false, error: '扩展后台无响应' });
      });
    });
  }

  // ---------- 工具 ----------
  function clean(s) {
    return (s || '').replace(/\s+/g, ' ').trim();
  }
  function val(id) {
    var el = root.querySelector(id);
    return el ? el.value.trim() : '';
  }
  function setVal(id, text) {
    var el = root.querySelector(id);
    if (el) { el.value = text == null ? '' : String(text); }
  }
  function shortTime(iso) {
    if (!iso) { return ''; }
    return String(iso).slice(0, 16).replace('T', ' ');
  }
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function canonicalJobUrl(href) {
    try {
      var u = new URL(href);
      var keep = {};
      ['id', 'jobId', 'securityId'].forEach(function (k) {
        if (u.searchParams.get(k)) { keep[k] = u.searchParams.get(k); }
      });
      u.search = '';
      Object.keys(keep).forEach(function (k) { u.searchParams.set(k, keep[k]); });
      var out = u.href;
      if (out.endsWith('/')) { out = out.slice(0, -1); }
      return out;
    } catch (e) {
      return href;
    }
  }

  // ---------- 页面数据提取 ----------
  function firstText(selectors) {
    for (var i = 0; i < selectors.length; i++) {
      var nodes = document.querySelectorAll(selectors[i]);
      for (var j = 0; j < nodes.length; j++) {
        var t = clean(nodes[j].innerText || nodes[j].textContent);
        if (t) { return t; }
      }
    }
    return '';
  }
  function longestText(selectors, maxLen) {
    var best = '';
    maxLen = maxLen || 50000;
    for (var i = 0; i < selectors.length; i++) {
      var nodes = document.querySelectorAll(selectors[i]);
      for (var j = 0; j < nodes.length; j++) {
        var t = clean(nodes[j].innerText || nodes[j].textContent);
        if (t.length > best.length) { best = t; }
      }
    }
    return best.slice(0, maxLen);
  }
  function parseTitle() {
    var t = document.title || '';
    var body = t.replace(/_BOSS直聘\s*$/, '').replace(/\s*BOSS直聘\s*$/, '').replace(/-\s*招聘信息\s*$/, '');
    if (!body) { return null; }
    var parts = body.split('_');
    return { position: parts[0] || '', company: parts[1] || '' };
  }

  function isJobPage() {
    var href = location.href;
    if (/\/job_detail\//.test(href) || /\/web\/geek\/job/.test(href) || /job\?id=/.test(href)) { return true; }
    return document.querySelectorAll('.salary, .job-sec-text, .job-primary, [class*="job-title"]').length >= 2;
  }

  function extractJob() {
    var position = firstText([
      'h1.name', '.job-title h1', '.job-title', '.name h1', '[class*="job-title"] h1',
      '.info-primary .name', '.job-primary .name', 'h1'
    ]);
    var company = firstText([
      '.company-info h3 a', '.company-name', 'a[ka="job-detail-company"]',
      '.job-detail-company .name', '.boss-info .name', '.company-info .name',
      '[class*="company"] a[class*="name"]'
    ]);
    var salary = firstText(['.job-primary .salary', '.salary', '[class*="salary"]']);
    var location = firstText([
      '.location-address', '.job-location', '.job-area',
      '.job-primary .info-primary p', '[class*="location"]', '[class*="address"]'
    ]);
    var jdText = longestText([
      '.job-sec-text', '.job-detail-section', '[class*="job-detail"] .text',
      '[data-selector="job-detail-body"]', '.job-detail', '[class*="job-description"]'
    ]);

    var fromTitle = parseTitle();
    if (!position && fromTitle) { position = fromTitle.position; }
    if (!company && fromTitle) { company = fromTitle.company; }
    if (!company && fromTitle) { company = fromTitle.company; }

    if (!/[\dKk．.]/.test(salary)) { salary = ''; }
    if ((location || '').length > 80) { location = ''; }

    return {
      company: company,
      position: position,
      salary: salary,
      location: location,
      jd_text: jdText,
      job_url: canonicalJobUrl(location.href)
    };
  }

  // ---------- 浮层面板 ----------
  var host = document.createElement('div');
  host.id = HOST_ID;
  document.documentElement.appendChild(host);
  var shadow = host.attachShadow({ mode: 'open' });

  shadow.innerHTML =
    '<style>' +
    ':host{all:initial}' +
    '*{box-sizing:border-box;font-family:"Microsoft YaHei",system-ui,sans-serif}' +
    '.fab{position:fixed;right:24px;bottom:24px;z-index:2147483000;width:52px;height:52px;border-radius:26px;' +
    'background:#07c160;color:#fff;font-size:22px;border:none;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.28)}' +
    '.fab:hover{transform:scale(1.06)}' +
    '.panel{position:fixed;right:20px;bottom:20px;z-index:2147483001;width:400px;max-height:86vh;overflow:auto;' +
    'background:#fff;color:#222;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.25);display:none;flex-direction:column}' +
    '.panel.open{display:flex}' +
    '.head{display:flex;align-items:center;gap:8px;padding:10px 12px;background:#07c160;color:#fff;' +
    'border-radius:12px 12px 0 0;font-size:14px;font-weight:600;position:sticky;top:0}' +
    '.head .sp{flex:1}' +
    '.head button{background:rgba(255,255,255,.22);color:#fff;border:none;border-radius:6px;' +
    'width:24px;height:24px;cursor:pointer;font-size:14px;line-height:1}' +
    '.body{padding:10px 12px;display:flex;flex-direction:column;gap:8px}' +
    '.status{font-size:12px;border-radius:6px;padding:6px 8px;background:#f3f4f6;color:#555;line-height:1.5}' +
    '.status.ok{background:#e8f7ee;color:#0a7a3d}' +
    '.status.err{background:#fdecea;color:#b42318}' +
    '.field label{display:block;font-size:12px;color:#888;margin-bottom:3px}' +
    '.field input,.field select,.field textarea{width:100%;border:1px solid #d9d9d9;border-radius:6px;' +
    'padding:6px 8px;font-size:13px;color:#222;background:#fff;outline:none}' +
    '.field textarea{resize:vertical;min-height:70px;font-family:inherit;line-height:1.5}' +
    '.field input:focus,.field select:focus,.field textarea:focus{border-color:#07c160}' +
    '.row2{display:flex;gap:8px}.row2 .field{flex:1}' +
    '.btn{display:block;width:100%;border:none;border-radius:8px;padding:9px;font-size:14px;' +
    'cursor:pointer;background:#07c160;color:#fff;font-weight:600}' +
    '.btn:hover{filter:brightness(1.05)}' +
    '.btn:disabled{opacity:.5;cursor:not-allowed}' +
    '.btn.ghost{background:#f3f4f6;color:#555;font-weight:500}' +
    '.result{display:none;border:1px solid #d9f0e2;background:#f5fcf8;border-radius:8px;padding:8px;gap:6px;flex-direction:column}' +
    '.result.show{display:flex}' +
    '.result .msg{font-size:13px;color:#0a7a3d}' +
    '.result textarea{width:100%;border:1px solid #cfe9da;border-radius:6px;padding:6px;font-size:13px;' +
    'min-height:64px;resize:vertical;font-family:inherit;line-height:1.5}' +
    '.mini{display:flex;gap:6px}' +
    '.mini .btn{font-size:12px;padding:5px 8px;width:auto;flex:1}' +
    '.recent{margin-top:2px}' +
    '.recent h4{font-size:12px;color:#666;margin:6px 0 4px}' +
    '.rec{display:flex;align-items:center;gap:6px;font-size:12px;padding:5px 6px;border-radius:6px;background:#fafafa;margin-bottom:4px}' +
    '.rec .info{flex:1;min-width:0}' +
    '.rec .info b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
    '.rec .info span{color:#999}' +
    '.rec .dup{color:#d97706}' +
    '.rec button{border:none;background:#fdecea;color:#b42318;border-radius:5px;padding:2px 6px;cursor:pointer;font-size:12px}' +
    '.foot{font-size:11px;color:#aaa;text-align:center;padding:6px 10px;border-top:1px solid #f0f0f0}' +
    '.empty{font-size:12px;color:#aaa;padding:4px 2px}' +
    '.toast{position:fixed;right:24px;bottom:92px;z-index:2147483002;max-width:360px;padding:8px 12px;' +
    'border-radius:8px;font-size:13px;line-height:1.5;box-shadow:0 4px 14px rgba(0,0,0,.22);display:none}' +
    '.toast.show{display:block}' +
    '.toast.ok{background:#e8f7ee;color:#0a7a3d}' +
    '.toast.err{background:#fdecea;color:#b42318}' +
    '.toast.warn{background:#fff7e6;color:#b25e09}' +
    '.auto-row{display:flex;align-items:center;gap:6px;font-size:13px;color:#333;cursor:pointer;user-select:none}' +
    '.auto-row input{width:auto;margin:0}' +
    '.auto-note{font-size:12px;color:#555;line-height:1.5;min-height:14px}' +
    '.auto-note.ok{color:#0a7a3d}.auto-note.err{color:#b42318}.auto-note.warn{color:#b25e09}' +
    '</style>' +
    '<button class="fab" id="xlb-fab" title="小林投递助手">📦</button>' +
    '<div class="panel" id="xlb-panel">' +
    '<div class="head"><span>📦 小林投递助手</span><span class="sp"></span>' +
    '<button id="xlb-min">–</button><button id="xlb-close">×</button></div>' +
    '<div class="body">' +
    '<div class="status" id="xlb-status">检测本地服务…</div>' +
    '<label class="auto-row"><input type="checkbox" id="xlb-auto" checked>' +
    '🤖 打招呼后自动记录（公司/职位/薪资/JD）</label>' +
    '<div class="auto-note" id="xlb-auto-note"></div>' +
    '<div class="field"><label>公司（必填）</label><input id="xlb-company" placeholder="自动提取，可修改"></div>' +
    '<div class="field"><label>职位</label><input id="xlb-position" placeholder="自动提取，可修改"></div>' +
    '<div class="row2">' +
    '<div class="field"><label>薪资</label><input id="xlb-salary" placeholder="如 20-40K"></div>' +
    '<div class="field"><label>地点</label><input id="xlb-location" placeholder="如 北京"></div>' +
    '</div>' +
    '<div class="field"><label>JD 原文（存档用）</label><textarea id="xlb-jd" placeholder="自动提取，可修改"></textarea></div>' +
    '<div class="field"><label>关联简历</label><select id="xlb-resume"><option value="">加载中…</option></select></div>' +
    '<button class="btn" id="xlb-record">记录到工具箱（去重）</button>' +
    '<div class="result" id="xlb-result">' +
    '<div class="msg" id="xlb-result-msg"></div>' +
    '<textarea id="xlb-greeting" placeholder="打招呼文稿会出现在这里，请人工确认后再发送"></textarea>' +
    '<div class="mini">' +
    '<button class="btn" id="xlb-copy">📋 复制打招呼语</button>' +
    '<button class="btn ghost" id="xlb-del">🗑 删除这条记录</button>' +
    '</div>' +
    '</div>' +
    '<div class="recent"><h4>最近记录（5 条）</h4><div id="xlb-recent"></div></div>' +
    '</div>' +
    '<div class="foot">AI 只起草 · 发送前请人工确认 · 记录保存在本地小林工具箱</div>' +
    '</div>' +
    '<div class="toast" id="xlb-toast"></div>';

  var root = shadow;
  var fab = root.getElementById('xlb-fab');
  var panel = root.getElementById('xlb-panel');
  var statusEl = root.getElementById('xlb-status');
  var resumeSel = root.getElementById('xlb-resume');
  var recordBtn = root.getElementById('xlb-record');
  var resultBox = root.getElementById('xlb-result');
  var resultMsg = root.getElementById('xlb-result-msg');
  var greetingBox = root.getElementById('xlb-greeting');
  var recentBox = root.getElementById('xlb-recent');
  var lastSnapshotId = null;
  var autoChk = root.getElementById('xlb-auto');
  var autoNoteEl = root.getElementById('xlb-auto-note');
  var autoToastEl = root.getElementById('xlb-toast');

  function setStatus(text, cls) {
    statusEl.textContent = text;
    statusEl.className = 'status' + (cls ? ' ' + cls : '');
  }

  fab.addEventListener('click', function () {
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) { onOpen(); }
  });
  root.getElementById('xlb-close').addEventListener('click', function () { panel.classList.remove('open'); });
  root.getElementById('xlb-min').addEventListener('click', function () { panel.classList.remove('open'); });

  function onOpen() {
    setStatus('检测本地服务…');
    var job = extractJob();
    if (!isJobPage() && !job.company && !job.position) {
      setStatus('⚠ 当前页面未识别到职位详情，可手动填写后记录，或打开职位详情页。', '');
    }
    setVal('#xlb-company', job.company);
    setVal('#xlb-position', job.position);
    setVal('#xlb-salary', job.salary);
    setVal('#xlb-location', job.location);
    setVal('#xlb-jd', job.jd_text);
    cacheJobContext(job);
    hideResult();
    loadResumes();
    loadRecent();
    bridge('BRIDGE_HEALTH').then(function (r) {
      if (r.ok) { setStatus('✅ 本地服务已连接（小林工具箱 v' + (r.data.version || '') + '）', 'ok'); }
      else { setStatus('❌ 无法连接本地服务：' + r.error + '。请先启动后端，并检查扩展配置里的 Token。', 'err'); }
    });
  }

  function hideResult() {
    resultBox.classList.remove('show');
    lastSnapshotId = null;
  }

  function loadResumes() {
    bridge('BRIDGE_LIST_RESUMES').then(function (r) {
      resumeSel.innerHTML = '';
      if (!r.ok || !r.data || !r.data.length) {
        var o1 = document.createElement('option');
        o1.value = '';
        o1.textContent = '无简历，请先在工具箱创建';
        resumeSel.appendChild(o1);
        return;
      }
      var active = null;
      r.data.forEach(function (res) {
        var o = document.createElement('option');
        o.value = String(res.id);
        o.textContent = '#' + res.slot + ' ' + (res.version_name || res.filename || ('简历' + res.id));
        resumeSel.appendChild(o);
        if (res.is_active && active == null) { active = res.id; }
      });
      if (active != null) { resumeSel.value = String(active); }
    });
  }

  function loadRecent() {
    bridge('BRIDGE_LIST_RECORDS').then(function (r) {
      recentBox.innerHTML = '';
      if (!r.ok || !r.data || !r.data.length) {
        recentBox.innerHTML = '<div class="empty">暂无记录</div>';
        return;
      }
      r.data.forEach(function (row) {
        var snap = row.snapshot || {};
        var app = row.application || {};
        var div = document.createElement('div');
        div.className = 'rec';
        var info = document.createElement('div');
        info.className = 'info';
        var b = document.createElement('b');
        b.textContent = (snap.company || '?') + ' · ' + (snap.position || '');
        var s = document.createElement('span');
        s.textContent = shortTime(snap.created_at) + (app.status ? ' · ' + app.status : '');
        info.appendChild(b);
        info.appendChild(s);
        var del = document.createElement('button');
        del.textContent = '✕';
        del.title = '删除这条记录';
        del.addEventListener('click', function () {
          if (!window.confirm('删除该记录？（快照与投递记录一并删除）')) { return; }
          bridge('BRIDGE_DELETE_RECORD', { snapshotId: snap.id }).then(function (resp) {
            if (resp.ok) { loadRecent(); if (lastSnapshotId === snap.id) { hideResult(); } }
            else { window.alert('删除失败：' + resp.error); }
          });
        });
        div.appendChild(info);
        div.appendChild(del);
        recentBox.appendChild(div);
      });
    });
  }

  recordBtn.addEventListener('click', function () {
    var company = val('#xlb-company');
    if (!company) { window.alert('请填写公司名称'); return; }
    if (!resumeSel.value) { window.alert('请先在工具箱创建简历（或在面板选择简历）'); return; }
    recordBtn.disabled = true;
    var payload = {
      job_url: canonicalJobUrl(location.href),
      company: company,
      position: val('#xlb-position'),
      salary: val('#xlb-salary'),
      location: val('#xlb-location'),
      source: 'boss-zhipin',
      jd_text: val('#xlb-jd'),
      resume_id: parseInt(resumeSel.value, 10) || null,
      generate_greeting: true
    };
    bridge('BRIDGE_RECORD_JOB', payload).then(function (r) {
      recordBtn.disabled = false;
      if (!r.ok) {
        window.alert('记录失败：' + r.error);
        return;
      }
      var d = r.data || {};
      lastSnapshotId = d.snapshot_id || null;
      if (d.duplicate) {
        resultMsg.textContent = 'ℹ 该职位已记录过（应用 #' + d.application_id + '），未重复写入。';
        greetingBox.value = d.greeting || '';
      } else {
        resultMsg.textContent = '✅ 已记录（应用 #' + d.application_id + '）。请人工核对下方打招呼语后再发送。';
        greetingBox.value = d.greeting || '';
      }
      resultBox.classList.add('show');
      loadRecent();
    });
  });

  root.getElementById('xlb-copy').addEventListener('click', function () {
    var text = greetingBox.value;
    if (!text) { window.alert('还没有可复制的打招呼语'); return; }
    function fallbackCopy() {
      var ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); window.alert('已复制（旧方案）'); }
      catch (e) { window.alert('复制失败，请手动选中复制'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { window.alert('已复制打招呼语，请到 BOSS 聊天框粘贴并人工发送'); }, fallbackCopy);
    } else {
      fallbackCopy();
    }
  });

  root.getElementById('xlb-del').addEventListener('click', function () {
    if (!lastSnapshotId) { window.alert('暂无已记录条目可删除'); return; }
    if (!window.confirm('删除这条记录？（快照与投递记录一并删除）')) { return; }
    bridge('BRIDGE_DELETE_RECORD', { snapshotId: lastSnapshotId }).then(function (r) {
      if (r.ok) { hideResult(); loadRecent(); }
      else { window.alert('删除失败：' + r.error); }
    });
  });
  // ================= 自动记录：打招呼 / 发消息后自动入库（v0.2） =================
  // 触发：聊天列表出现“自己发出的消息”（item-mine 等）或发送动作后列表新增消息
  // 上下文：职位详情页直取 -> 聊天区职位卡片/链接 -> 最近访问过的职位页缓存
  var AUTO_RECORD_GAP_MS = 10 * 60 * 1000; // 同一岗位 10 分钟内只自动记录一次
  var CACHE_TTL_MS = 2 * 60 * 60 * 1000;   // 职位上下文缓存有效期 2 小时
  var autoRecordOn = true;
  var autoArmedAt = 0;                     // 最近一次“发送动作”时间戳
  var autoBaseline = -1;                   // 发送前的消息条数（兜底检测用）
  var autoHandledKeys = {};                // 已处理消息指纹（防重复触发）
  var autoLastOkAt = {};                   // job_url/公司 -> 最近自动记录时间
  var autoArmedCard = null;                // 发送时对应的职位卡片（列表页聊天场景）
  var chatObserverRegistry = [];
  var autoToastTimer = null;
  var SALARY_RE = /(\d{1,3}(?:\.\d)?\s*[Kk]\s*[-~—–至到]\s*\d{1,3}(?:\s*\.\d)?\s*[Kk]|\d{1,3}\s*[-~—–至到]\s*\d{1,3}\s*[Kk])/;

  function setAutoNote(text, cls) {
    if (!autoNoteEl) { return; }
    autoNoteEl.textContent = text || '';
    autoNoteEl.className = 'auto-note' + (cls ? ' ' + cls : '');
  }

  function showAutoToast(text, cls) {
    if (!autoToastEl) { return; }
    autoToastEl.textContent = text;
    autoToastEl.className = 'toast show' + (cls ? ' ' + cls : '');
    if (autoToastTimer) { clearTimeout(autoToastTimer); }
    autoToastTimer = setTimeout(function () {
      autoToastEl.className = 'toast';
    }, 6000);
  }

  // ---------- 职位上下文缓存（职位页 -> 聊天页跨页复用） ----------
  function cacheJobContext(job) {
    try {
      if (!job || !job.company || !job.jd_text) { return; }
      if (typeof chrome === 'undefined' || !chrome.storage || !chrome.storage.session) { return; }
      chrome.storage.session.set({
        xlb_last_job_ctx: {
          company: job.company,
          position: job.position || '',
          salary: job.salary || '',
          location: job.location || '',
          job_url: job.job_url || '',
          jd_text: String(job.jd_text || '').slice(0, 20000),
          cached_at: Date.now()
        }
      });
    } catch (e) { /* 缓存失败不影响主流程 */ }
  }

  function readCachedJobContext() {
    return new Promise(function (resolve) {
      try {
        if (typeof chrome === 'undefined' || !chrome.storage || !chrome.storage.session) { resolve(null); return; }
        chrome.storage.session.get('xlb_last_job_ctx', function (d) {
          var c = d && d.xlb_last_job_ctx;
          if (c && c.company && c.job_url && (Date.now() - (c.cached_at || 0)) < CACHE_TTL_MS) {
            resolve(c);
          } else {
            resolve(null);
          }
        });
      } catch (e) { resolve(null); }
    });
  }

  // ---------- 职位信息解析（聊天页/职位卡片通用） ----------
  function parseJobText(txt) {
    var out = { company: '', position: '', salary: '', location: '' };
    var lines = String(txt || '').split('\n');
    var metaRe = /(经验|学历|本科|大专|硕士|博士|在校|应届|融资|上市|未融资|不需要|天内|在线|今日|昨日|刚刚|活跃|沟通|交换|查看|简历|职位详情|立即沟通|打招呼|发送|消息|招聘|BOSS|直聘|举报|收藏|分享|附近|地铁|写字楼|园区|人\s|人$|~\s*\d)/;
    var positionIdx = -1;
    var salaryIdx = -1;
    for (var i = 0; i < lines.length && i < 14; i++) {
      var line = clean(lines[i]);
      if (!line || line.length > 60) { continue; }
      if (positionIdx < 0 && !SALARY_RE.test(line) && !metaRe.test(line) && line.length <= 40) {
        positionIdx = i;
      }
      if (salaryIdx < 0 && SALARY_RE.test(line)) {
        salaryIdx = i;
        var m = line.match(SALARY_RE);
        if (m) { out.salary = m[1] || m[0]; }
        var parts = line.split(/[·•|]/);
        for (var p = 0; p < parts.length; p++) {
          var pp = clean(parts[p]);
          if (pp && !SALARY_RE.test(pp) && !out.location && /[\u4e00-\u9fa5]{2,16}$/.test(pp) && pp.length <= 16 && !metaRe.test(pp)) {
            out.location = pp;
          }
        }
        continue;
      }
      if (salaryIdx >= 0 && !out.company && !SALARY_RE.test(line) && !metaRe.test(line)) {
        out.company = line;
      }
    }
    if (positionIdx >= 0) { out.position = clean(lines[positionIdx]); }
    return out;
  }

  function readJobCard(cardEl) {
    var out = { company: '', position: '', salary: '', location: '', job_url: '', jd_text: '' };
    if (!cardEl) { return out; }
    var q = function (sel) {
      var el = cardEl.querySelector(sel);
      return el ? clean(el.innerText || el.textContent) : '';
    };
    out.position = q('.job-name, [class*="job-name"], .position-name, h3');
    out.company = q('.company-name, [class*="company-name"], .boss-name, .company');
    out.salary = q('.salary, [class*="salary"]');
    var a = cardEl.querySelector('a[href*="/job?id="], a[href*="job_detail"], a[href*="geek/job"]');
    if (a) { out.job_url = canonicalJobUrl(a.href); }
    if (!out.company || !out.position || !out.salary) {
      var parsed = parseJobText(cardEl.innerText || cardEl.textContent);
      if (!out.company) { out.company = parsed.company; }
      if (!out.position) { out.position = parsed.position; }
      if (!out.salary) { out.salary = parsed.salary; }
      if (!out.location) { out.location = parsed.location; }
    }
    return out;
  }

  function scoreJobCtx(c) {
    var s = 0;
    if (c.company) { s += 3; }
    if (c.position) { s += 3; }
    if (c.salary) { s += 2; }
    if (c.job_url) { s += 2; }
    return s;
  }

  // 聊天页 / 职位列表页：从可见的职位卡片、聊天头部职位横幅或岗位链接解析上下文
  function extractChatJobCard() {
    var candidates = [];
    var holderSel = [
      '[class*="position-content"]',
      '[class*="job-card"]',
      '[class*="job-intro"]',
      '[class*="chat-job"]',
      'li.job-card-box'
    ];
    for (var s = 0; s < holderSel.length; s++) {
      var nodes = document.querySelectorAll(holderSel[s]);
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        var txt = clean(el.innerText || el.textContent);
        if (txt.length < 6 || txt.length > 5000) { continue; }
        if (el.offsetParent === null && !el.closest('.chat-message, [class*="chat"]')) { continue; }
        var c = readJobCard(el);
        if (c.company || c.position || c.salary) { candidates.push(c); }
      }
    }
    // 刚点过“立即沟通”的职位卡片优先（列表页聊天场景）
    if (autoArmedCard) {
      var armed = readJobCard(autoArmedCard);
      if (armed.company || armed.position) { candidates.unshift(armed); }
    }
    // 兜底：页面里带薪资文本、可见的岗位链接所在容器
    if (!candidates.length) {
      var anchors = document.querySelectorAll('a[href*="/job?id="], a[href*="job_detail"], a[href*="geek/job"]');
      for (var k = 0; k < anchors.length && candidates.length === 0; k++) {
        var a = anchors[k];
        if (a.offsetParent === null && !a.closest('.chat-message, [class*="chat"], .im-list')) { continue; }
        var walk = a;
        for (var d = 0; d < 7; d++, walk = walk.parentElement) {
          if (!walk || walk === document.body) { break; }
          var t = clean(walk.innerText || walk.textContent);
          if (t.length > 5 && t.length < 5000 && SALARY_RE.test(t)) {
            var c2 = readJobCard(walk);
            if (!c2.job_url) { c2.job_url = canonicalJobUrl(a.href); }
            candidates.push(c2);
            break;
          }
        }
      }
    }
    if (!candidates.length) {
      // 最后兜底：聊天页头部职位名/公司单点文本
      var pn = document.querySelector('[class*="position-content"] .position-name, [class*="chat"] .position-name, .chat-header .job-name, .position-name');
      var cn = document.querySelector('[class*="chat"] .company-name, .chat-header .company-name, [class*="chat"] .name-box span:nth-child(2)');
      var stub = { company: '', position: '', salary: '', location: '', job_url: canonicalJobUrl(location.href), jd_text: '' };
      if (pn) { stub.position = clean(pn.innerText || pn.textContent); }
      if (cn) { stub.company = clean(cn.innerText || cn.textContent); }
      if (stub.company && stub.position) { candidates.push(stub); }
    }
    candidates.sort(function (x, y) { return scoreJobCtx(y) - scoreJobCtx(x); });
    return candidates[0] || null;
  }

  // 多级解析：职位详情页直取 > 当前页聊天卡片/缓存 > 最近职位页缓存
  function resolveAutoContext() {
    return new Promise(function (resolve) {
      var inline = extractJob();
      var jobUrlLike = location.href.indexOf('/job_detail/') >= 0 || location.href.indexOf('/web/geek/job') >= 0 || location.href.indexOf('job?') >= 0;
      var inlineOk = jobUrlLike && inline.company && (inline.jd_text || inline.position || inline.salary);
      if (inlineOk) {
        cacheJobContext(inline);
        resolve(inline);
        return;
      }
      var fromPage = extractChatJobCard();
      if (fromPage && fromPage.company) {
        if (fromPage.job_url && !fromPage.jd_text) { cacheJobContext(fromPage); }
        resolve(fromPage);
        return;
      }
      readCachedJobContext().then(function (cached) {
        if (cached) { resolve(cached); } else { resolve(null); }
      });
    });
  }

  // ---------- 消息内容与“是否自己发送”判断 ----------
  function extractSentText(el) {
    var textEl = el.querySelector
      ? el.querySelector('.message-content .text, .chat-message-content, .msg-content, .content .text, .text')
      : null;
    var txt = textEl ? clean(textEl.innerText || textEl.textContent) : '';
    if (!txt) { txt = clean(el.innerText || el.textContent); }
    return txt;
  }

  function isSelfMessageEl(el) {
    if (!el || el.nodeType !== 1 || !el.classList || !el.classList.contains) { return false; }
    var cls = el.classList;
    if (!cls.contains('message-item')) { return false; }
    if (cls.contains('item-friend') || cls.contains('friend')) { return false; }
    if (/notice|tips|system|time|date|separator|divider|sys/i.test(el.className)) { return false; }
    if (cls.contains('item-mine') || cls.contains('item-self') || cls.contains('mine') || cls.contains('self')) { return true; }
    var txt = extractSentText(el);
    return txt.length > 0 && txt.length <= 2000;
  }

  function isBottomish(node, container) {
    var n = node;
    for (var depth = 0; n && depth < 5; depth++, n = n.parentNode) {
      if (n === container) { break; }
    }
    var parent = node.parentNode;
    if (!parent || !parent.children) { return true; }
    var kids = parent.children;
    for (var i = kids.length - 1; i >= Math.max(0, kids.length - 3); i--) {
      if (kids[i] === node || kids[i].contains(node)) { return true; }
    }
    return false;
  }

  // ---------- 自动记录主流程 ----------
  function handleSelfMessageSent(el) {
    if (!autoRecordOn || !el || el.nodeType !== 1) { return; }
    var text = extractSentText(el);
    var fp = text ? text.slice(0, 200) : 'no-text';
    if (autoHandledKeys[fp] && (Date.now() - autoHandledKeys[fp]) < 30000) { return; } // 同内容 30 秒去重
    autoHandledKeys[fp] = Date.now();
    var explicit = /item-mine|item-self|(^|\s)(mine|self)(\s|$)/i.test(' ' + el.className + ' ');
    if (!explicit) {
      // 非明确“自己”样式时，需要刚发生过发送动作才可信
      if (!autoArmedAt || (Date.now() - autoArmedAt) > 6000) { return; }
    }
    resolveAutoContext().then(function (ctx) {
      if (!ctx || !ctx.company) {
        setAutoNote('⚠ 未能识别当前岗位，已跳过自动记录（可在职位详情页发送，或点 📦 手动记录）', 'warn');
        return;
      }
      autoRecordJob(ctx, text);
    });
  }

  function autoRecordJob(ctx, sentText) {
    var key = ctx.job_url || (ctx.company + '|' + (ctx.position || ''));
    var now = Date.now();
    if (autoLastOkAt[key] && (now - autoLastOkAt[key]) < AUTO_RECORD_GAP_MS) { return; } // 节流
    autoLastOkAt[key] = now;
    var payload = {
      job_url: ctx.job_url || canonicalJobUrl(location.href),
      company: ctx.company,
      position: ctx.position || '',
      salary: ctx.salary || '',
      location: ctx.location || '',
      source: 'boss-zhipin',
      jd_text: ctx.jd_text || '',
      resume_id: null,
      generate_greeting: false,
      greeting: sentText || ''
    };
    bridge('BRIDGE_RECORD_JOB', payload).then(function (r) {
      var tag = (ctx.company || '') + (ctx.position ? ' · ' + ctx.position : '');
      if (r.ok) {
        var dup = !!(r.data && r.data.duplicate);
        if (r.data && r.data.snapshot_id) { lastSnapshotId = r.data.snapshot_id; }
        var msg = dup
          ? ('该岗位已自动记录过（应用 #' + (r.data && r.data.application_id) + '），未重复写入：' + tag)
          : ('已自动记录：' + tag);
        setAutoNote((dup ? 'ℹ ' : '✅ ') + msg, dup ? 'warn' : 'ok');
        showAutoToast('📦 ' + msg, dup ? 'warn' : 'ok');
        if (panel.classList.contains('open')) { loadRecent(); }
      } else {
        var why = String(r.error || '');
        if (/401/.test(why)) { why = 'Token 无效，请在扩展弹窗检查'; }
        else if (/简历/.test(why)) { why = '请先在小林工具箱创建简历'; }
        else if (/fetch|Failed|网络|服务/i.test(why)) { why = '本地服务未启动或不可达'; }
        setAutoNote('❌ 自动记录失败：' + why, 'err');
        showAutoToast('📦 自动记录失败：' + why, 'err');
      }
    });
  }

  // ---------- 发送动作监听（用于提高识别可信度 + 兜底） ----------
  function armAutoSend() {
    autoArmedAt = Date.now();
    autoBaseline = document.querySelectorAll('.message-item, .im-list li').length;
  }

  function pollBaselineFallback() {
    if (!autoArmedAt || (Date.now() - autoArmedAt) > 7000) { autoArmedAt = 0; return; }
    var items = document.querySelectorAll('li.message-item, .message-item');
    if (!items.length || items.length <= autoBaseline) { return; }
    for (var i = items.length - 1; i >= 0; i--) {
      if (isSelfMessageEl(items[i])) {
        autoArmedAt = 0;
        handleSelfMessageSent(items[i]);
        return;
      }
    }
  }

  function setupAutoListeners() {
    if (setupAutoListeners.done) { return; }
    setupAutoListeners.done = true;
    document.addEventListener('keydown', function (ev) {
      if (!autoRecordOn || ev.key !== 'Enter' || ev.shiftKey || ev.ctrlKey || ev.metaKey || ev.altKey) { return; }
      var t = ev.target;
      if (t && (t.id === 'chat-input' || (t.isContentEditable && t.closest && t.closest('[class*="chat"], .im-list')))) {
        armAutoSend();
      }
    }, true);
    document.addEventListener('click', function (ev) {
      if (!autoRecordOn) { return; }
      var t = ev.target;
      if (!t || !t.closest) { return; }
      var chatBtn = t.closest('a.op-btn-chat, a[class*="op-btn-chat"], a[class*="btn-startchat"]');
      if (chatBtn) {
        var card = chatBtn.closest('li.job-card-box');
        if (card) { autoArmedCard = card; }
        armAutoSend();
        return;
      }
      var send = t.closest('.btn-send, [class*="btn-send"], [class*="send-btn"], [class*="icon-send"]');
      if (!send && t.nodeType === 1 && (t.tagName === 'BUTTON' || t.tagName === 'A')) {
        var label = clean(t.textContent);
        if (/^(立即沟通|在线沟通|打招呼|发送|发消息|发送消息)$/.test(label)) { send = t; }
      }
      if (send) { armAutoSend(); }
    }, true);
  }

  // ---------- 聊天列表观察（自动打招呼 / 点发送后落库） ----------
  function findChatLists() {
    var out = [];
    var list = document.querySelectorAll('.chat-message .im-list, .chat-message ul, .im-list, .message-list, [class*="im-list"]');
    for (var i = 0; i < list.length; i++) {
      if (list[i].querySelector('li.message-item, .message-item')) { out.push(list[i]); }
    }
    return out;
  }

  function onChatMutations(mutations, obs) {
    var entry = null;
    for (var i = 0; i < chatObserverRegistry.length; i++) {
      if (chatObserverRegistry[i].obs === obs) { entry = chatObserverRegistry[i]; break; }
    }
    if (!entry) { return; }
    var listEl = entry.el;
    var itemsNow = listEl.querySelectorAll('.message-item').length;
    var shrank = entry.lastCount !== undefined && itemsNow < entry.lastCount;
    entry.lastCount = itemsNow;
    if (shrank) { entry.booted = false; return; } // 切换会话，列表被清空重挂载
    if (!entry.booted) {
      entry.booted = true;
      // 首次挂载多为历史消息；除非刚点过“立即沟通/发送”（首条可能是自动打招呼）
      if (!autoArmedAt || (Date.now() - autoArmedAt) > 8000) { return; }
    }
    for (var m = 0; m < mutations.length; m++) {
      var mu = mutations[m];
      if (mu.type !== 'childList' || !mu.addedNodes) { continue; }
      for (var j = 0; j < mu.addedNodes.length; j++) {
        var n = mu.addedNodes[j];
        if (n.nodeType !== 1) { continue; }
        var el = null;
        if (n.classList && n.classList.contains && n.classList.contains('message-item')) {
          el = n;
        } else if (n.querySelectorAll) {
          var mine = n.querySelectorAll('.message-item.item-mine, .message-item.item-self, .message-item:not(.item-friend)');
          if (mine.length) { el = mine[mine.length - 1]; }
        }
        if (!el || !isBottomish(el, listEl)) { continue; }
        if (isSelfMessageEl(el)) {
          handleSelfMessageSent(el);
          autoArmedAt = 0;
        }
      }
    }
  }

  function syncChatObservers() {
    var lists = findChatLists();
    for (var i = 0; i < lists.length; i++) {
      var listEl = lists[i];
      var found = false;
      for (var k = 0; k < chatObserverRegistry.length; k++) {
        if (chatObserverRegistry[k].el === listEl) { found = true; break; }
      }
      if (found) { continue; }
      var obs = new MutationObserver(onChatMutations);
      obs.observe(listEl, { childList: true, subtree: true });
      chatObserverRegistry.push({ el: listEl, obs: obs, booted: false, lastCount: undefined });
    }
    for (var d = chatObserverRegistry.length - 1; d >= 0; d--) {
      if (!document.contains(chatObserverRegistry[d].el)) {
        chatObserverRegistry[d].obs.disconnect();
        chatObserverRegistry.splice(d, 1);
      }
    }
  }

  // ---------- 开关与启动 ----------
  function loadAutoPref() {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get({ autoRecord: true }, function (d) {
          autoRecordOn = d.autoRecord !== false;
          if (autoChk) { autoChk.checked = autoRecordOn; }
        });
      }
    } catch (e) { /* ignore */ }
  }

  function startAutoRecord() {
    loadAutoPref();
    setupAutoListeners();
    syncChatObservers();
    setInterval(syncChatObservers, 2000);
    setInterval(pollBaselineFallback, 900);
    // 打开职位页时预热上下文缓存（发消息时可跨页复用）
    if (isJobPage()) {
      var j0 = extractJob();
      if (j0 && j0.company && j0.jd_text) { cacheJobContext(j0); }
    }
    if (autoChk) {
      autoChk.addEventListener('change', function () {
        autoRecordOn = autoChk.checked;
        try {
          if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
            chrome.storage.local.set({ autoRecord: autoRecordOn });
          }
        } catch (e) { /* ignore */ }
        if (autoRecordOn) {
          setAutoNote('✅ 已开启：在 BOSS 发送消息 / 打招呼后将自动记录', 'ok');
        } else {
          setAutoNote('⏸ 已暂停自动记录（面板“记录到工具箱”仍可用）', 'warn');
        }
      });
    }
  }

  startAutoRecord();
})();