import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import CompetitionPage from './CompetitionPage'
import '@testing-library/jest-dom/vitest' // Fix TypeScript/Vitest expectations if needed

// We mock fetch for the test
global.fetch = vi.fn() as any

describe('CompetitionPage', () => {
  it('affiche les données mockées si l\'API échoue (mode local/MVP)', async () => {
    // Simule une erreur réseau ou un échec de l'API
    (global.fetch as any).mockRejectedValueOnce(new Error('API Down'))

    render(
      <MemoryRouter initialEntries={['/competition/999']}>
        <Routes>
          <Route path="/competition/:id" element={<CompetitionPage />} />
        </Routes>
      </MemoryRouter>
    )

    // Vérifie qu'il y a un chargement initial
    expect(screen.getByText('Chargement...')).toBeInTheDocument()

    // Attend la résolution et l'affichage des données mockées
    await waitFor(() => {
      expect(screen.getByText('Marathon de Dakar 2026')).toBeInTheDocument()
    })

    // Vérifie quelques éléments de l'UI
    expect(screen.getByText('14 Février 2026')).toBeInTheDocument()
    expect(screen.getByText('Corniche Ouest, Dakar')).toBeInTheDocument()
    expect(screen.getByText('Tarif unique : 1500 FCFA / photo')).toBeInTheDocument()
  })
})
