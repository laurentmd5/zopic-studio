import { api } from './api'

export const authService = {
  requestOtp: async (phone_number: string) => {
    const response = await api.post('/auth/request-otp', { phone_number })
    return response.data
  },
  
  verifyOtp: async (phone_number: string, code: string) => {
    // URLSearchParams for form-data if needed, but our backend might accept JSON for /verify ?
    // Let's check backend schema. OAuth2PasswordRequestForm usually requires form data.
    const formData = new URLSearchParams()
    formData.append('username', phone_number) // OAuth2 maps phone to username
    formData.append('password', code) // OTP is the password

    const response = await api.post('/auth/verify', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/auth/me')
    return response.data
  }
}
