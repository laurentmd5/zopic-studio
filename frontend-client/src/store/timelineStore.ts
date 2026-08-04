import { create } from 'zustand'
import axios from 'axios'

export interface CompetitionTimelineItem {
  id: string | number
  name: string
  date: string
  sport: string
  location: string
  photos_count: number
  cover_photo_url: string
}

export interface YearGroup {
  year: number
  competitions: CompetitionTimelineItem[]
}

interface TimelineState {
  timeline: YearGroup[]
  totalCompetitions: number
  totalPhotos: number
  message: string
  isLoading: boolean
  error: string | null
  expandedYears: number[]
  
  fetchTimeline: (sessionId?: string) => Promise<void>
  toggleYear: (year: number) => void
}

export const useTimelineStore = create<TimelineState>((set) => ({
  timeline: [],
  totalCompetitions: 0,
  totalPhotos: 0,
  message: '',
  isLoading: false,
  error: null,
  expandedYears: [],

  fetchTimeline: async (sessionId = 'guest-123') => {
    set({ isLoading: true, error: null })
    try {
      const response = await axios.get('http://localhost:8000/api/v1/athletes/me/timeline', {
        headers: {
          'X-Session-ID': sessionId,
          // 'Authorization': `Bearer ${token}` // TODO: handle JWT token automatically if logged in
        }
      })
      
      const { timeline, total_competitions, total_photos, message } = response.data
      
      // Expand the current year by default if there is one
      const currentYear = new Date().getFullYear()
      const defaultExpanded = timeline.some((g: YearGroup) => g.year === currentYear) 
        ? [currentYear] 
        : (timeline.length > 0 ? [timeline[0].year] : [])

      set({ 
        timeline, 
        totalCompetitions: total_competitions, 
        totalPhotos: total_photos, 
        message,
        expandedYears: defaultExpanded,
        isLoading: false
      })
    } catch (error: any) {
      console.error('Error fetching timeline', error)
      set({ error: error.message || 'Une erreur est survenue', isLoading: false })
    }
  },

  toggleYear: (year: number) => set((state) => ({
    expandedYears: state.expandedYears.includes(year)
      ? state.expandedYears.filter(y => y !== year)
      : [...state.expandedYears, year]
  }))
}))
