/**
 * 投递记录Store
 */

import { defineStore } from "pinia"
import type { Application, ApplicationStatus } from "@/types/api"

interface ApplicationState {
  applications: Application[]
  loading: boolean
  error: string | null
}

export const useApplicationStore = defineStore("application", {
  state: (): ApplicationState => ({
    applications: [],
    loading: false,
    error: null
  }),

  getters: {
    totalCount: (state): number => state.applications.length,
    
    interviewCount: (state): number => {
      return state.applications.filter(a => a.status === "面试中").length
    },
    
    offerCount: (state): number => {
      return state.applications.filter(a => a.status === "Offer").length
    },
    
    pendingCount: (state): number => {
      return state.applications.filter(a => a.status === "待处理").length
    },
    
    recentApplications: (state): Application[] => {
      return state.applications.slice(0, 5)
    },
    
    getByStatus: (state) => (status: ApplicationStatus | "all"): Application[] => {
      if (status === "all") return state.applications
      return state.applications.filter(a => a.status === status)
    },
    
    stats: (state) => {
      return {
        total: state.applications.length,
        pending: state.applications.filter(a => a.status === "待处理").length,
        applied: state.applications.filter(a => a.status === "已投递").length,
        interview: state.applications.filter(a => a.status === "面试中").length,
        offer: state.applications.filter(a => a.status === "Offer").length,
        rejected: state.applications.filter(a => a.status === "已拒绝").length
      }
    }
  },

  actions: {
    addApplication(data: Omit<Application, "id">): { success: boolean; duplicate?: boolean } {
      // 检查重复
      const duplicate = this.applications.find(
        a => a.company.toLowerCase() === data.company.toLowerCase()
      )

      if (duplicate) {
        return { success: false, duplicate: true }
      }

      const newApplication: Application = {
        ...data,
        id: Date.now(),
        created_at: new Date().toISOString()
      }

      this.applications.unshift(newApplication)
      return { success: true }
    },

    updateApplication(id: number, data: Partial<Application>): void {
      const index = this.applications.findIndex(a => a.id === id)
      if (index !== -1) {
        this.applications[index] = {
          ...this.applications[index],
          ...data,
          updated_at: new Date().toISOString()
        }
      }
    },

    updateStatus(id: number, status: ApplicationStatus): void {
      this.updateApplication(id, { status })
    },

    updateNotes(id: number, notes: string): void {
      this.updateApplication(id, { notes })
    },

    deleteApplication(id: number): void {
      this.applications = this.applications.filter(a => a.id !== id)
    },

    clearAll(): void {
      this.applications = []
    },

    setLoading(loading: boolean): void {
      this.loading = loading
    },

    setError(error: string | null): void {
      this.error = error
    },

    // 从API加载
    async loadApplications(): Promise<void> {
      this.loading = true
      this.error = null

      try {
        const { applicationApi } = await import("@/api")
        const response = await applicationApi.list()
        this.applications = response || []
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载失败"
      } finally {
        this.loading = false
      }
    },

    // 创建投递记录
    async createApplication(data: {
      company: string
      position?: string
      status?: ApplicationStatus
      salary?: string
    }): Promise<void> {
      this.loading = true
      this.error = null

      try {
        const { applicationApi } = await import("@/api")
        const response = await applicationApi.create(data)
        this.applications.unshift(response)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "创建失败"
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
