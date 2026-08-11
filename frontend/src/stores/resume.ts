/**
 * 简历Store
 */

import { defineStore } from "pinia"
import type { Resume } from "@/types/api"

interface ResumeState {
  resumes: Record<number, Resume>
  activeSlot: number | null
  loading: boolean
  error: string | null
}

export const useResumeStore = defineStore("resume", {
  state: (): ResumeState => ({
    resumes: {},
    activeSlot: 1,
    loading: false,
    error: null
  }),

  getters: {
    activeResume: (state): Resume | null => {
      if (state.activeSlot && state.resumes[state.activeSlot]) {
        return state.resumes[state.activeSlot]
      }
      return null
    },
    
    resumeCount: (state): number => {
      return Object.keys(state.resumes).length
    },
    
    hasResume: (state): boolean => {
      return Object.keys(state.resumes).length > 0
    },
    
    getResumeBySlot: (state) => (slot: number): Resume | null => {
      return state.resumes[slot] || null
    }
  },

  actions: {
    setActiveSlot(slot: number): void {
      if (slot >= 1 && slot <= 4) {
        this.activeSlot = slot
      }
    },

    addResume(slot: number, resume: Resume): void {
      this.resumes[slot] = {
        ...resume,
        slot,
        updated_at: new Date().toISOString()
      }
      
      // 如果是第一个简历，自动设为active
      if (!this.activeSlot) {
        this.activeSlot = slot
      }
    },

    updateResume(slot: number, data: Partial<Resume>): void {
      if (this.resumes[slot]) {
        this.resumes[slot] = {
          ...this.resumes[slot],
          ...data,
          updated_at: new Date().toISOString()
        }
      }
    },

    deleteResume(slot: number): void {
      delete this.resumes[slot]
      
      if (this.activeSlot === slot) {
        // 选择下一个可用的槽位
        const slots = Object.keys(this.resumes).map(Number)
        this.activeSlot = slots.length > 0 ? Math.min(...slots) : null
      }
    },

    clearAll(): void {
      this.resumes = {}
      this.activeSlot = null
    },

    setLoading(loading: boolean): void {
      this.loading = loading
    },

    setError(error: string | null): void {
      this.error = error
    },

    // 加载简历列表
    async loadResumes(): Promise<void> {
      this.loading = true
      this.error = null
      
      try {
        const { resumeApi } = await import("@/api")
        const response = await resumeApi.list()
        
        this.resumes = {}
        for (let i = 1; i <= 4; i++) {
          if (response[i]) {
            this.resumes[i] = response[i]
          }
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载失败"
      } finally {
        this.loading = false
      }
    },

    // 上传简历
    async uploadResume(file: File, slot: number, versionName?: string): Promise<void> {
      this.loading = true
      this.error = null
      
      try {
        const { resumeApi } = await import("@/api")
        await resumeApi.upload(file, slot, versionName)
        
        this.addResume(slot, {
          slot,
          filename: file.name,
          version_name: versionName || file.name,
          file_type: file.name.split(".").pop() || "unknown",
          file_size: file.size
        })
      } catch (error) {
        this.error = error instanceof Error ? error.message : "上传失败"
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
