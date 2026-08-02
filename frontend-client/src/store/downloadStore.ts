import { create } from 'zustand'

interface DownloadState {
  purchasedPhotos: any[]
  setPurchasedPhotos: (photos: any[]) => void
}

export const useDownloadStore = create<DownloadState>((set) => ({
  purchasedPhotos: [],
  setPurchasedPhotos: (photos) => set({ purchasedPhotos: photos })
}))
