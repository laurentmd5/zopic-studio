import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore } from './useThemeStore'

describe('Theme Store', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    // Reset state since initial state depends on window.matchMedia and localStorage
    useThemeStore.setState({ theme: 'light' })
  })

  it('devrait changer le theme avec toggleTheme', () => {
    const store = useThemeStore.getState()
    store.toggleTheme()
    
    expect(useThemeStore.getState().theme).toBe('dark')
    expect(localStorage.getItem('zopic-theme')).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('devrait définir un theme specifique avec setTheme', () => {
    const store = useThemeStore.getState()
    store.setTheme('dark')
    
    expect(useThemeStore.getState().theme).toBe('dark')
    expect(localStorage.getItem('zopic-theme')).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
