import { create } from 'zustand'

interface AuthState {
  token: string | null
  user: any | null // We will type this properly later
  setToken: (token: string) => void
  setUser: (user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('zopic-token'),
  user: null,
  setToken: (token) => {
    localStorage.setItem('zopic-token', token)
    set({ token })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('zopic-token')
    set({ token: null, user: null })
  },
}))
