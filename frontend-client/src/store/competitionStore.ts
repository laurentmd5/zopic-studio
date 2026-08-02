import { create } from 'zustand'

interface CompetitionState {
  competition: any | null
  setCompetition: (data: any) => void
}

export const useCompetitionStore = create<CompetitionState>((set) => ({
  competition: null,
  setCompetition: (data) => set({ competition: data })
}))
