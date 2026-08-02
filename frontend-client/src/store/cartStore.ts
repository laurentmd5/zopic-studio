import { create } from 'zustand'

interface CartState {
  items: any[]
  total: number
  addItem: (item: any) => void
  removeItem: (id: number) => void
  clearCart: () => void
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  total: 0,
  addItem: (item) => set((state) => ({ 
    items: [...state.items, item],
    total: state.total + (item.price || 1500) 
  })),
  removeItem: (id) => set((state) => {
    const newItems = state.items.filter(i => i.id !== id)
    return {
      items: newItems,
      total: newItems.reduce((acc, curr) => acc + (curr.price || 1500), 0)
    }
  }),
  clearCart: () => set({ items: [], total: 0 })
}))
