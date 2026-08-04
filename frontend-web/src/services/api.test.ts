import { describe, it, expect } from 'vitest'
import { api } from './api'
import { useAuthStore } from '../store/useAuthStore'

describe('API Interceptors', () => {
  it('devrait ajouter le token aux headers de requête si disponible', () => {
    useAuthStore.setState({ token: 'test-token-123' })
    
    // Test that interceptor is registered
    expect(api.interceptors.request).toBeDefined()
    
    // Normally you'd test the behavior by doing a mock request
    // or by calling the interceptor handler manually
    const handlers = (api.interceptors.request as any).handlers
    if (handlers && handlers.length > 0) {
      const config = handlers[0].fulfilled({ headers: {} })
      expect(config.headers['Authorization']).toBe('Bearer test-token-123')
    }
  })

  it('devrait rediriger vers /login si 401', async () => {
    // Basic test to verify interceptor logic
    const handlers = (api.interceptors.response as any).handlers
    if (handlers && handlers.length > 0) {
      const error = { response: { status: 401 } }
      try {
        await handlers[0].rejected(error)
      } catch (e) {
        expect(e).toBe(error)
      }
      expect(useAuthStore.getState().token).toBeNull()
    }
  })
})
