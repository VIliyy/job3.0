/**
 * 信息拆解 mock 层测试：验证真实业务可用的状态机流转
 * normal（一路绿灯）/ regenerate（闸门重生成版本+1）
 */
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import { decomposeMock } from "./mock"
import { realApi } from "./index"
import apiClient from "../index"

vi.mock("../index", () => ({
  default: {
    post: vi.fn()
  }
}))

// mock 内部有真实延时（模拟异步处理），此处用真实等待
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

  const GATE_A_WAIT = 1200 // createTask(120) + S0(30+900) + getTask(100)
const GATE_B_WAIT = 1500 // decide(150) + S1(30+1200) + getTask(100)
const GATE_C_WAIT = 1500 // decide(150) + S2(30+1200) + getTask(100)
const DONE_WAIT = 1000 // decide(150) + S3(30+700) + getTask(100)

describe("decompose mock 状态机", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it(
    "normal 场景：一路绿灯跑完并导出",
    async () => {
      const task = await decomposeMock.createTask({
        content: "要求 3 年 Python 经验。价格 39.99 美元。评分 4.5 星。有海外仓。",
        target: "评估产品可行性"
      })
      expect(task.state).toBe("DRAFT")

      // S0 → 闸门A
      await sleep(GATE_A_WAIT)
      let detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("BRIEF_REVIEW")
      expect(detail.contracts.S0.inferences[0].content).toContain("评估产品可行性")

      // 确认闸门A → S1 → 闸门B
      await decomposeMock.decideGate(detail.gates.A.id, { action: "approve" })
      await sleep(GATE_B_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("FACTS_REVIEW")
      expect(detail.contracts.S1.facts.length).toBeGreaterThan(0)
      expect(detail.contracts.S1.facts[0].anchor).toContain("第")

      // 确认闸门B → S2 → 闸门C
      await decomposeMock.decideGate(detail.gates.B.id, { action: "approve" })
      await sleep(GATE_C_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("INSIGHT_REVIEW")
      const s2 = detail.contracts.S2
      expect(s2.inferences.length).toBeGreaterThan(0)
      // 结论必须引用事实
      const usp = s2.inferences.find((i: any) => i.type === "usp")
      expect(usp).toBeTruthy()
      expect(usp!.evidence.length).toBeGreaterThan(0)

      // 确认闸门C → S3 → DONE
      await decomposeMock.decideGate(detail.gates.C.id, { action: "approve" })
      await sleep(DONE_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("DONE")
      expect(detail.contracts.S3.inferences.length).toBeGreaterThan(0)

      // 导出包含结论与事实
      const { markdown } = await decomposeMock.exportTask(task.id)
      expect(markdown).toContain("信息拆解报告")
      expect(markdown).toContain("结论")
      expect(markdown).toContain("F-001")
    },
    30000
  )

  it(
    "regenerate 场景：闸门B 重生成后契约 version+1 且下游失效",
    async () => {
      const task = await decomposeMock.createTask({ content: "要求英语六级。包住。薪资 8k-12k。" })
      await sleep(GATE_A_WAIT)
      let detail = await decomposeMock.getTask(task.id)
      await decomposeMock.decideGate(detail.gates.A.id, { action: "approve" })
      await sleep(GATE_B_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("FACTS_REVIEW")

      // 提交意见重生成
      await decomposeMock.decideGate(detail.gates.B.id, { action: "regenerate", note: "第三条事实不准确" })
      await sleep(GATE_B_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("FACTS_REVIEW")
      expect(detail.contracts.S1.version).toBe(2)
      expect(detail.contracts.S2).toBeUndefined() // 下游已失效
      expect(detail.gates.B.note).toContain("不准确")

      // 再次确认 → 正常继续
      await decomposeMock.decideGate(detail.gates.B.id, { action: "approve" })
      await sleep(GATE_C_WAIT)
      detail = await decomposeMock.getTask(task.id)
      expect(detail.state).toBe("INSIGHT_REVIEW")
    },
    30000
  )

  it(
    "delete 场景：删除任务后列表清空且详情不可取",
    async () => {
      const task = await decomposeMock.createTask({
        content: "要求 3 年 Python 经验。价格 39.99 美元。"
      })
      await sleep(GATE_A_WAIT)
      let list = await decomposeMock.listTasks()
      expect(list.length).toBe(1)

      const res = await decomposeMock.deleteTask(task.id)
      expect(res.ok).toBe(true)
      list = await decomposeMock.listTasks()
      expect(list.length).toBe(0)
      await expect(decomposeMock.getTask(task.id)).rejects.toThrow("任务不存在")
    },
    30000
  )

})

describe("decompose real API contract", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("sends from_stage when rerunning a task", async () => {
    vi.mocked(apiClient.post).mockResolvedValue({} as never)

    await realApi.rerun(7, "S1")

    expect(apiClient.post).toHaveBeenCalledWith(
      "/decompose/tasks/7/rerun",
      { from_stage: "S1" }
    )
  })

  it("opens SSE through the configured API base instead of localhost", () => {
    const sources: Array<{ url: string }> = []
    class EventSourceStub {
      static latest: EventSourceStub | undefined
      url: string
      constructor(url: string) {
        this.url = url
        sources.push(this)
        EventSourceStub.latest = this
      }
      addEventListener() {}
      close() {}
    }
    vi.stubGlobal("EventSource", EventSourceStub)

    realApi.subscribeEvents("7", {})

    expect(sources[0]?.url).toBe("/api/decompose/tasks/7/events")
  })

  it("does not parse native EventSource network errors as server JSON", () => {
    class EventSourceStub {
      static latest: EventSourceStub | undefined
      listeners = new Map<string, (event: Event) => void>()
      constructor(_url: string) {
        EventSourceStub.latest = this
      }
      addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
        this.listeners.set(type, listener as (event: Event) => void)
      }
      close() {}
    }
    vi.stubGlobal("EventSource", EventSourceStub)
    const onError = vi.fn()
    realApi.subscribeEvents("7", { error: onError })

    expect(() => EventSourceStub.latest?.listeners.get("error")?.(new Event("error"))).not.toThrow()
    expect(onError).not.toHaveBeenCalled()
  })

  it("delivers server error events with their structured message", () => {
    class EventSourceStub {
      static latest: EventSourceStub | undefined
      listeners = new Map<string, (event: Event) => void>()
      constructor(_url: string) {
        EventSourceStub.latest = this
      }
      addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
        this.listeners.set(type, listener as (event: Event) => void)
      }
      close() {}
    }
    vi.stubGlobal("EventSource", EventSourceStub)
    const onError = vi.fn()
    realApi.subscribeEvents("7", { error: onError })

    const payload = { type: "error", task_id: "7", message: "task failed" }
    EventSourceStub.latest?.listeners.get("error")?.(new MessageEvent("error", { data: JSON.stringify(payload) }))

    expect(onError).toHaveBeenCalledWith(payload)
  })
})
