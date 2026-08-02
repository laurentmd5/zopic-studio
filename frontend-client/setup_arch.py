import os

def create_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

def setup_arch():
    base = r"E:\ZoPic Studio\frontend-client\src"
    
    # 1. CSS Variables
    css_content = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --color-primary: #5D4037; /* Marron foncé */
  --color-accent: #827717; /* Vert Olive */
  --color-background: #121212; /* Dark mode par défaut */
  --color-surface: #1E1E1E;
  --color-text: #FFFFFF;
  --color-text-muted: #B3B3B3;
  --color-border: #333333;
  --color-error: #CF6679;
  --color-success: #03DAC6;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}

a {
  color: inherit;
  text-decoration: none;
}
"""
    create_file(os.path.join(base, "index.css"), css_content)

    # 2. Stores (Zustand)
    stores = {
        "authStore.ts": """import { create } from 'zustand'

interface AuthState {
  token: string | null
  setToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('guest-token'),
  setToken: (token) => {
    localStorage.setItem('guest-token', token)
    set({ token })
  },
  logout: () => {
    localStorage.removeItem('guest-token')
    set({ token: null })
  }
}))
""",
        "competitionStore.ts": """import { create } from 'zustand'

interface CompetitionState {
  competition: any | null
  setCompetition: (data: any) => void
}

export const useCompetitionStore = create<CompetitionState>((set) => ({
  competition: null,
  setCompetition: (data) => set({ competition: data })
}))
""",
        "searchStore.ts": """import { create } from 'zustand'

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
""",
        "cartStore.ts": """import { create } from 'zustand'

interface CartState {
  items: any[]
  total: number
  addItem: (item: any) => void
  removeItem: (id: number) => void
  clearCart: () => void
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  total: 0,
  addItem: (item) => set((state) => ({ 
    items: [...state.items, item],
    total: state.total + (item.price || 1500) 
  })),
  removeItem: (id) => set((state) => {
    const newItems = state.items.filter(i => i.id !== id)
    return {
      items: newItems,
      total: newItems.reduce((acc, curr) => acc + (curr.price || 1500), 0)
    }
  }),
  clearCart: () => set({ items: [], total: 0 })
}))
""",
        "paymentStore.ts": """import { create } from 'zustand'

type PaymentStatus = 'idle' | 'processing' | 'success' | 'error'

interface PaymentState {
  status: PaymentStatus
  setStatus: (status: PaymentStatus) => void
}

export const usePaymentStore = create<PaymentState>((set) => ({
  status: 'idle',
  setStatus: (status) => set({ status })
}))
""",
        "downloadStore.ts": """import { create } from 'zustand'

interface DownloadState {
  purchasedPhotos: any[]
  setPurchasedPhotos: (photos: any[]) => void
}

export const useDownloadStore = create<DownloadState>((set) => ({
  purchasedPhotos: [],
  setPurchasedPhotos: (photos) => set({ purchasedPhotos: photos })
}))
"""
    }

    for filename, content in stores.items():
        create_file(os.path.join(base, "store", filename), content)

    # 3. App.tsx with Routing
    app_content = """import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import CompetitionPage from './pages/CompetitionPage'
import SearchPage from './pages/SearchPage'
import CheckoutPage from './pages/CheckoutPage'
import DownloadsPage from './pages/DownloadsPage'

function App() {
  return (
    <>
      <Toaster position="top-center" />
      <Router>
        <Routes>
          <Route path="/competition/:id" element={<CompetitionPage />} />
          <Route path="/competition/:id/search" element={<SearchPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/downloads" element={<DownloadsPage />} />
          {/* Redirect to a demo competition for MVP testing */}
          <Route path="*" element={<Navigate to="/competition/1" replace />} />
        </Routes>
      </Router>
    </>
  )
}

export default App
"""
    create_file(os.path.join(base, "App.tsx"), app_content)

    # 4. Dummy Pages
    pages = ["CompetitionPage", "SearchPage", "CheckoutPage", "DownloadsPage"]
    for p in pages:
        create_file(os.path.join(base, "pages", f"{p}.tsx"), f"export default function {p}() {{ return <div>{p}</div> }}")

if __name__ == "__main__":
    setup_arch()
