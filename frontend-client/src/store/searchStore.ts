import { create } from 'zustand'

type SearchStateEnum = 'idle' | 'loading' | 'success' | 'empty' | 'error'

interface SearchState {
  state: SearchStateEnum
  results: any[]
  setSearchState: (state: SearchStateEnum) => void
  setResults: (results: any[]) => void
}

export const useSearchStore = create<SearchState>((set) => ({
  state: 'idle',
  results: [],
  setSearchState: (state) => set({ state }),
  setResults: (results) => set({ results })
}))
