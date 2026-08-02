import { describe, it, expect, beforeEach } from 'vitest'
import { useCartStore } from './cartStore'

describe('Cart Store', () => {
  beforeEach(() => {
    // Reset state before each test
    useCartStore.getState().clearCart()
  })

  it('devrait ajouter une photo et calculer le total correctement', () => {
    const store = useCartStore.getState()
    store.addItem({ id: 1, url: 'img1.jpg', price: 1500 })
    
    expect(useCartStore.getState().items.length).toBe(1)
    expect(useCartStore.getState().total).toBe(1500)
  })

  it('devrait supprimer une photo et déduire le prix', () => {
    const store = useCartStore.getState()
    store.addItem({ id: 1, url: 'img1.jpg', price: 1500 })
    store.addItem({ id: 2, url: 'img2.jpg', price: 1500 })
    
    expect(useCartStore.getState().total).toBe(3000)
    
    useCartStore.getState().removeItem(1)
    
    expect(useCartStore.getState().items.length).toBe(1)
    expect(useCartStore.getState().total).toBe(1500)
  })
})
