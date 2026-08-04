import { create } from 'zustand'

export interface PackConfig {
  quantity: number
  price_xof: number
  label: string
}

export interface AppliedPackDetail {
  label: string
  count: number
  total: number
}

interface CartState {
  items: any[]
  total: number
  savings: number
  appliedPacksDetails: AppliedPackDetail[]
  
  // Configuration
  packsEnabled: boolean
  packsConfig: PackConfig[]
  unitPrice: number
  
  // Actions
  addItem: (item: any) => void
  removeItem: (id: number) => void
  clearCart: () => void
  setConfig: (enabled: boolean, packs: PackConfig[], unitPrice: number) => void
}

const recalculateTotal = (
  itemsCount: number, 
  packsEnabled: boolean, 
  packsConfig: PackConfig[], 
  unitPrice: number
) => {
  let total = 0
  let savings = 0
  let appliedPacksDetails: AppliedPackDetail[] = []
  const originalTotal = itemsCount * unitPrice
  
  if (!packsEnabled || packsConfig.length === 0 || itemsCount === 0) {
    return {
      total: originalTotal,
      savings: 0,
      appliedPacksDetails: []
    }
  }

  // Trier par quantité décroissante (Glouton)
  const sortedPacks = [...packsConfig].sort((a, b) => b.quantity - a.quantity)
  let remaining = itemsCount

  for (const pack of sortedPacks) {
    if (pack.quantity > 0 && remaining >= pack.quantity) {
      const count = Math.floor(remaining / pack.quantity)
      const cost = count * pack.price_xof
      total += cost
      remaining -= count * pack.quantity
      
      appliedPacksDetails.push({
        label: pack.label,
        count: count,
        total: cost
      })
    }
  }

  // Prix unitaire pour le reste
  if (remaining > 0) {
    const cost = remaining * unitPrice
    total += cost
    appliedPacksDetails.push({
      label: `${remaining} photo(s) au prix unitaire`,
      count: 1, // on groupe le reste
      total: cost
    })
  }

  savings = originalTotal - total

  return {
    total,
    savings: savings > 0 ? savings : 0,
    appliedPacksDetails
  }
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  total: 0,
  savings: 0,
  appliedPacksDetails: [],
  
  // Default values
  packsEnabled: true, // For MVP demo
  packsConfig: [
    { quantity: 10, price_xof: 3500, label: "10 photos" },
    { quantity: 5, price_xof: 2000, label: "5 photos" }
  ],
  unitPrice: 1500,
  
  setConfig: (enabled, packs, price) => set((state) => {
    const calc = recalculateTotal(state.items.length, enabled, packs, price)
    return {
      packsEnabled: enabled,
      packsConfig: packs,
      unitPrice: price,
      ...calc
    }
  }),
  
  addItem: (item) => set((state) => {
    const newItems = [...state.items, item]
    const calc = recalculateTotal(newItems.length, state.packsEnabled, state.packsConfig, state.unitPrice)
    return { items: newItems, ...calc }
  }),
  
  removeItem: (id) => set((state) => {
    const newItems = state.items.filter(i => i.id !== id)
    const calc = recalculateTotal(newItems.length, state.packsEnabled, state.packsConfig, state.unitPrice)
    return { items: newItems, ...calc }
  }),
  
  clearCart: () => set({ items: [], total: 0, savings: 0, appliedPacksDetails: [] })
}))
