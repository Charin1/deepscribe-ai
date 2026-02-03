import axios from 'axios'
import { Project, Title, Plan, Draft, ExecutionStatus } from '../types'

const client = axios.create({ baseURL: '/api' })

export const api = {
    // Projects
    async getProjects(page = 1, perPage = 20) {
        const { data } = await client.get('/projects', { params: { page, per_page: perPage } })
        return data
    },

    async getProject(id: string): Promise<Project> {
        const { data } = await client.get(`/projects/${id}`)
        return data
    },

    async createProject(payload: object): Promise<Project> {
        const { data } = await client.post('/projects', payload)
        return data
    },

    async deleteProject(id: string): Promise<void> {
        await client.delete(`/projects/${id}`)
    },

    // Titles
    async generateTitles(projectId: string) {
        const { data } = await client.post(`/projects/${projectId}/generate-titles`)
        return data
    },

    async getTitles(projectId: string): Promise<{ titles: Title[] }> {
        const { data } = await client.get(`/projects/${projectId}/titles`)
        return data
    },

    async selectTitle(projectId: string, titleId: string): Promise<Project> {
        const { data } = await client.post(`/projects/${projectId}/select-title`, { title_id: titleId })
        return data
    },

    // Plan
    async generatePlan(projectId: string): Promise<Plan> {
        const { data } = await client.post(`/projects/${projectId}/generate-plan`)
        return data
    },

    async getPlan(projectId: string): Promise<Plan> {
        const { data } = await client.get(`/projects/${projectId}/plan`)
        return data
    },

    async updatePlan(projectId: string, sections: object[]): Promise<Plan> {
        const { data } = await client.put(`/projects/${projectId}/plan`, { sections })
        return data
    },

    async approvePlan(projectId: string): Promise<Project> {
        const { data } = await client.post(`/projects/${projectId}/approve-plan`)
        return data
    },

    // Execution
    async startExecution(projectId: string) {
        const { data } = await client.post(`/projects/${projectId}/run`)
        return data
    },

    async restartExecution(projectId: string) {
        const { data } = await client.post(`/projects/${projectId}/restart`)
        return data
    },

    async getExecutionStatus(projectId: string): Promise<ExecutionStatus> {
        const { data } = await client.get(`/projects/${projectId}/status`)
        return data
    },

    // Draft
    async getDraft(projectId: string): Promise<Draft> {
        const { data } = await client.get(`/projects/${projectId}/result`)
        return data
    },

    async approveDraft(projectId: string): Promise<Draft> {
        const { data } = await client.post(`/projects/${projectId}/approve`)
        return data
    },

    async updateDraft(projectId: string, contentMarkdown: string): Promise<Draft> {
        const { data } = await client.put(`/projects/${projectId}/result`, { content_markdown: contentMarkdown })
        return data
    },

    async exportDraft(projectId: string, format: string): Promise<{ content: string; format: string }> {
        const { data } = await client.post(`/projects/${projectId}/export`, { format })
        return data
    },
}
