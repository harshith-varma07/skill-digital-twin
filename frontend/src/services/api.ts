import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        await useAuthStore.getState().refreshAccessToken()
        const token = useAuthStore.getState().accessToken
        
        if (token) {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }
      } catch {
        useAuthStore.getState().logout()
      }
    }
    
    return Promise.reject(error)
  }
)

export default api

// API service functions
export const authService = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: Record<string, unknown>) =>
    api.post('/auth/register', data),
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
}

export const userService = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data: Record<string, unknown>) => api.put('/users/me', data),
  uploadResume: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/users/me/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getProfileCompleteness: () => api.get('/users/me/profile-completeness'),
}

export const skillService = {
  getSkills: (params?: Record<string, unknown>) => api.get('/skills/', { params }),
  getUserSkills: () => api.get('/skills/user'),
  addUserSkill: (data: Record<string, unknown>) => api.post('/skills/user', data),
  updateUserSkill: (skillId: number, masteryLevel: number) =>
    api.put(`/skills/user/${skillId}?mastery_level=${masteryLevel}`),
  removeUserSkill: (skillId: number) => api.delete(`/skills/user/${skillId}`),
  extractSkills: (text: string, context?: string) =>
    api.post('/skills/extract', { text, context }),
  getCategories: () => api.get('/skills/categories'),
}

export const digitalTwinService = {
  getProfile: () => api.get('/digital-twin/profile'),
  getGapAnalysis: (targetRoleId?: number) =>
    api.get('/digital-twin/gap-analysis', { params: { target_role_id: targetRoleId } }),
  getGapAnalysisForSkills: (targetSkills: number[]) =>
    api.post('/digital-twin/gap-analysis/skills', targetSkills),
  updateProfile: (data: Record<string, unknown>) =>
    api.post('/digital-twin/update', data),
  recordInteraction: (event: Record<string, unknown>) =>
    api.post('/digital-twin/interaction', event),
  getSummary: () => api.get('/digital-twin/summary'),
  getVisualizationData: () => api.get('/digital-twin/visualization-data'),
}

export const assessmentService = {
  getAssessments: (params?: Record<string, unknown>) =>
    api.get('/assessments/', { params }),
  getAssessment: (id: number) => api.get(`/assessments/${id}`),
  createDiagnostic: (data: Record<string, unknown>) =>
    api.post('/assessments/diagnostic', data),
  startAssessment: (id: number) => api.post(`/assessments/${id}/start`),
  submitAssessment: (id: number, responses: Record<string, unknown>[]) =>
    api.post(`/assessments/${id}/submit`, { responses }),
  getResults: (id: number) => api.get(`/assessments/${id}/results`),
  generatePracticeQuestions: (data: Record<string, unknown>) =>
    api.post('/assessments/practice-questions', data),
}

export const learningService = {
  getRoadmaps: (activeOnly?: boolean) =>
    api.get('/learning/roadmaps', { params: { active_only: activeOnly } }),
  getRoadmap: (id: number) => api.get(`/learning/roadmaps/${id}`),
  generateRoadmap: (data: Record<string, unknown>) =>
    api.post('/learning/roadmaps/generate', data),
  updateProgress: (roadmapId: number, data: Record<string, unknown>) =>
    api.post(`/learning/roadmaps/${roadmapId}/progress`, data),
  getNextResource: (roadmapId: number) =>
    api.get(`/learning/roadmaps/${roadmapId}/next`),
  deleteRoadmap: (id: number) => api.delete(`/learning/roadmaps/${id}`),
  searchYouTube: (data: Record<string, unknown>) =>
    api.post('/learning/youtube/search', data),
  markModuleComplete: (moduleId: number) =>
    api.post(`/learning/modules/${moduleId}/complete`),
  updateResourceProgress: (resourceId: number, progress: number) =>
    api.post(`/learning/resources/${resourceId}/progress?progress=${progress}`),
}

export const careerService = {
  getRoles: (params?: Record<string, unknown>) =>
    api.get('/careers/roles', { params }),
  getRole: (id: number) => api.get(`/careers/roles/${id}`),
  getAlignment: (roleId: number) => api.get(`/careers/alignment/${roleId}`),
  analyzeCareerOptions: (data: Record<string, unknown>) =>
    api.post('/careers/analyze', data),
  getRecommendations: () => api.get('/careers/recommendations'),
  setTargetRole: (roleId: number) =>
    api.post(`/careers/roles/${roleId}/set-target`),
}
