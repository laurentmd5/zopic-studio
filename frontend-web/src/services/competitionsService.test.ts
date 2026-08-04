import { describe, it, expect, vi } from 'vitest'
import type { Mock } from 'vitest'
import { competitionsService, storageService } from './competitionsService'
import { api } from './api'

vi.mock('./api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn()
  }
}))

describe('competitionsService', () => {
  it('devrait lister les événements', async () => {
    (api.get as Mock).mockResolvedValueOnce({ data: [] })
    const result = await competitionsService.getEvents()
    expect(result).toEqual([])
  })

  it('devrait créer un événement', async () => {
    (api.post as Mock).mockResolvedValueOnce({ data: { id: 1 } })
    const result = await competitionsService.createEvent({ name: 'Test', date: '2025-01-01' })
    expect(result.id).toBe(1)
  })

  it('devrait ajouter une épreuve', async () => {
    (api.post as Mock).mockResolvedValueOnce({ data: { id: 2 } })
    const result = await competitionsService.createÉpreuve(1, 'Course')
    expect(result.id).toBe(2)
  })
})

describe('storageService', () => {
  it('devrait récupérer une URL upload', async () => {
    (api.post as Mock).mockResolvedValueOnce({ data: { url: 'http://s3' } })
    const result = await storageService.getUploadUrl('img.jpg', 'image/jpeg')
    expect(result.url).toBe('http://s3')
  })
})
