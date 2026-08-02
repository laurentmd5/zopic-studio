import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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
