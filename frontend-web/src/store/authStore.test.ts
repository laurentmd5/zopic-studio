import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './useAuthStore'

describe('Auth Store', () => {
  beforeEach(() => {
    // Nettoie l'état avant chaque test
    useAuthStore.setState({ token: null, user: null })
    localStorage.clear()
  })

  it('devrait être déconnecté par défaut', () => {
    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
  })

  it('devrait connecter un photographe correctement', () => {
    const store = useAuthStore.getState()
    store.setToken('test_token')
    store.setUser({
      id: 1,
      phone: '771234567',
      role: 'photographer',
      name: 'Photographe Test'
    })
    
    const newState = useAuthStore.getState()
    expect(newState.token).toBe('test_token')
    expect(newState.user?.name).toBe('Photographe Test')
    expect(localStorage.getItem('zopic-token')).toBe('test_token')
  })

  it('devrait déconnecter l\'utilisateur', () => {
    const store = useAuthStore.getState()
    store.setToken('test_token')
    store.setUser({ name: 'test' })
    
    useAuthStore.getState().logout()
    
    const newState = useAuthStore.getState()
    expect(newState.token).toBeNull()
    expect(newState.user).toBeNull()
    expect(localStorage.getItem('zopic-token')).toBeNull()
  })
})
