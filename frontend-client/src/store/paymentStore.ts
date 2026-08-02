import { create } from 'zustand'

type PaymentStatus = 'idle' | 'processing' | 'success' | 'error'

interface PaymentState {
  status: PaymentStatus
  setStatus: (status: PaymentStatus) => void
}

export const usePaymentStore = create<PaymentState>((set) => ({
  status: 'idle',
  setStatus: (status) => set({ status })
}))
