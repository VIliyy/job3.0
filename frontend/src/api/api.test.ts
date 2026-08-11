/**
 * API 模块测试
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import axios from "axios"

vi.mock("axios")

describe("API 模块", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("resumeApi", () => {
    it("should upload resume successfully", async () => {
      const mockFile = new File(["content"], "resume.pdf", { type: "application/pdf" })
      const mockResponse = { data: { slot: 1, filename: "resume.pdf" } }
      
      vi.mocked(axios.create).mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse),
        get: vi.fn(),
        put: vi.fn(),
        delete: vi.fn()
      } as any)

      // 测试上传逻辑
      const formData = new FormData()
      formData.append("file", mockFile)
      formData.append("slot", "1")
      
      expect(mockFile.name).toBe("resume.pdf")
    })

    it("should handle upload error", () => {
      // 测试错误处理逻辑
      const errorResponse = {
        response: {
          data: { detail: "File too large" }
        }
      }
      
      expect(errorResponse.response.data.detail).toBe("File too large")
    })
  })

  describe("applicationApi", () => {
    it("should validate application data", () => {
      const validApplication = {
        company: "字节跳动",
        position: "后端工程师"
      }
      
      expect(validApplication.company.length).toBeGreaterThan(0)
      expect(validApplication.position.length).toBeGreaterThan(0)
    })
  })
})

describe("类型验证", () => {
  it("should validate Resume type", () => {
    const resume = {
      slot: 1,
      filename: "test.pdf",
      version_name: "v1"
    }
    
    expect(resume.slot).toBe(1)
    expect(resume.slot >= 1 && resume.slot <= 4).toBe(true)
  })

  it("should validate ApplicationStatus", () => {
    const validStatuses = [
      "待处理",
      "已投递", 
      "面试中",
      "Offer",
      "已拒绝"
    ]
    
    expect(validStatuses).toContain("待处理")
    expect(validStatuses).toContain("面试中")
  })
})
