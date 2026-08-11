/**
 * 简历Store测试
 */

import { describe, it, expect, beforeEach } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { useResumeStore } from "@/stores/resume"

describe("ResumeStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("should add resume to slot", () => {
    const store = useResumeStore()
    
    store.addResume(1, {
      slot: 1,
      filename: "resume.pdf",
      version_name: "v1"
    })
    
    expect(store.resumes[1]).toBeDefined()
    expect(store.resumes[1].filename).toBe("resume.pdf")
  })

  it("should set active slot", () => {
    const store = useResumeStore()
    
    store.addResume(1, { slot: 1, filename: "resume.pdf" })
    store.setActiveSlot(1)
    
    expect(store.activeSlot).toBe(1)
  })

  it("should delete resume", () => {
    const store = useResumeStore()
    
    store.addResume(1, { slot: 1, filename: "resume.pdf" })
    expect(Object.keys(store.resumes).length).toBe(1)
    
    store.deleteResume(1)
    expect(store.resumes[1]).toBeUndefined()
  })

  it("should count resumes correctly", () => {
    const store = useResumeStore()
    
    store.addResume(1, { slot: 1, filename: "r1.pdf" })
    store.addResume(2, { slot: 2, filename: "r2.pdf" })
    
    expect(store.resumeCount).toBe(2)
    expect(store.hasResume).toBe(true)
  })

  it("should clear all resumes", () => {
    const store = useResumeStore()
    
    store.addResume(1, { slot: 1, filename: "r1.pdf" })
    store.addResume(2, { slot: 2, filename: "r2.pdf" })
    store.clearAll()
    
    expect(store.resumeCount).toBe(0)
    expect(store.hasResume).toBe(false)
  })
})
