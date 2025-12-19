import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  email: string
  full_name: string
  education_level?: string
  field_of_study?: string
  years_of_experience: number
  interests: string[]
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
  loadUser: () => Promise<void>
}

interface RegisterData {
  email: string
  password: string
  full_name: string
  education_level?: string
  field_of_study?: string
  years_of_experience?: number
  interests?: string[]
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token, refresh_token } = response.data
          
          set({
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
          })
          
          // Load user data
          await get().loadUser()
        } finally {
          set({ isLoading: false })
        }
      },
      
      register: async (data: RegisterData) => {
        set({ isLoading: true })
        try {
          await api.post('/auth/register', data)
          // Auto login after registration
          await get().login(data.email, data.password)
        } finally {
          set({ isLoading: false })
        }
      },
      
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },
      
      refreshAccessToken: async () => {
        const { refreshToken } = get()
        if (!refreshToken) {
          get().logout()
          return
        }
        
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token } = response.data
          
          set({
            accessToken: access_token,
            refreshToken: refresh_token,
          })
        } catch {
          get().logout()
        }
      },
      
      loadUser: async () => {
        try {
          const response = await api.get('/users/me')
          set({ user: response.data })
        } catch {
          // If loading user fails, token might be invalid
          get().logout()
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
