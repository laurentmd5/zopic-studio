import { create } from 'zustand'

interface AuthState {
  token: string | null
  setToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('guest-token'),
  setToken: (token) => {
    localStorage.setItem('guest-token', token)
    set({ token })
  },
  logout: () => {
    localStorage.removeItem('guest-token')
    set({ token: null })
  }
}))
