import { api } from './api'

export interface CompetitionCreate {
  name: string
  date: string
  location?: string
  sport_type?: string
  price_per_photo?: number
  is_public?: boolean
  settings?: any
}

export const competitionsService = {
  getEvents: async () => {
    const response = await api.get('/competitions/')
    return response.data
  },
  
  createEvent: async (data: CompetitionCreate) => {
    const response = await api.post('/competitions/', data)
    return response.data
  },

  getEventDetails: async (eventId: string | number) => {
    const response = await api.get(`/competitions/${eventId}`)
    return response.data
  },

  createÉpreuve: async (eventId: string | number, name: string) => {
    const response = await api.post(`/competitions/${eventId}/epreuves`, { name })
    return response.data
  },

  addPhotoToÉpreuve: async (albumId: string | number, s3_object_key: string) => {
    const response = await api.post(`/competitions/epreuves/${albumId}/photos`, { s3_object_key })
    return response.data
  }
}

export const storageService = {
  getUploadUrl: async (filename: string, content_type: string, is_watermark: boolean = false) => {
    const response = await api.post('/storage/upload-url', {
      filename,
      content_type,
      is_watermark
    })
    return response.data
  },
  
  uploadToUrl: async (uploadUrl: string, file: File) => {
    // Note: Use direct axios instance to avoid our interceptors 
    // which might add Bearer token (S3/R2 presigned urls reject Authorization headers if they are not expected)
    const response = await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type
      }
    })
    if (!response.ok) {
      throw new Error('Failed to upload file to S3/R2')
    }
    return true
  }
}
