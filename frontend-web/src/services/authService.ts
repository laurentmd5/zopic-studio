import { api } from './api'

export const authService = {
  requestOtp: async (phone_number: string) => {
    const response = await api.post('/auth/request-otp', { phone_number })
    return response.data
  },
  
  verifyOtp: async (phone_number: string, code: string) => {
    const response = await api.post('/auth/verify', { 
      phone_number, 
      code 
    })
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/auth/me')
    return response.data
  }
}
