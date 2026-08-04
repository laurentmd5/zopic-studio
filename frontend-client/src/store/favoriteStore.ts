import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface FavoriteState {
  favorites: any[] // Store full photo objects instead of just IDs to easily display them
  sessionId: string
  toggleFavorite: (photo: any) => void
  isFavorite: (photoId: number) => boolean
  removeFavorites: (photoIds: number[]) => void
}

// Generate a simple UUID for guest session if not exists
const generateUUID = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return 'xxxx-xxxx-xxxx-xxxx'.replace(/[x]/g, () => (Math.random() * 16 | 0).toString(16))
}

export const useFavoriteStore = create<FavoriteState>()(
  persist(
    (set, get) => ({
      favorites: [],
      sessionId: generateUUID(),
      toggleFavorite: (photo) => {
        set((state) => {
          const exists = state.favorites.some((f) => f.id === photo.id)
          if (exists) {
            return { favorites: state.favorites.filter((f) => f.id !== photo.id) }
          } else {
            return { favorites: [...state.favorites, photo] }
          }
        })
      },
      isFavorite: (photoId) => {
        return get().favorites.some((f) => f.id === photoId)
      },
      removeFavorites: (photoIds) => {
        set((state) => ({
          favorites: state.favorites.filter((f) => !photoIds.includes(f.id))
        }))
      }
    }),
    {
      name: 'zopic_favorites',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
