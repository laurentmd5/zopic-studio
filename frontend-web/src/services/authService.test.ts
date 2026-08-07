import { describe, it, expect, vi } from 'vitest'
import type { Mock } from 'vitest'
import { authService } from './authService'
import { api } from './api'

vi.mock('./api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('authService', () => {
  it('devrait demander un OTP', async () => {
    (api.post as Mock).mockResolvedValueOnce({ data: { message: 'success' } })
    
    const result = await authService.requestOtp('771234567')
    expect(result.message).toBe('success')
    expect(api.post).toHaveBeenCalledWith('/auth/request-otp', { phone_number: '771234567' })
  })

  it('devrait vérifier un OTP', async () => {
    (api.post as Mock).mockResolvedValueOnce({ data: { access_token: '123' } })
    
    const result = await authService.verifyOtp('771234567', '0000')
    expect(result.access_token).toBe('123')
    expect(api.post).toHaveBeenCalledWith('/auth/verify', { phone_number: '771234567', code: '0000' })
  })

  it('devrait récupérer le profil', async () => {
    (api.get as Mock).mockResolvedValueOnce({ data: { id: 1 } })
    
    const result = await authService.getProfile()
    expect(result.id).toBe(1)
    expect(api.get).toHaveBeenCalledWith('/auth/me')
  })
})
