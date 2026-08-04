import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import CompetitionPage from './pages/CompetitionPage'
import SearchPage from './pages/SearchPage'
import CheckoutPage from './pages/CheckoutPage'
import PaymentPage from './pages/PaymentPage'
import DownloadsPage from './pages/DownloadsPage'
import FavoritesPage from './pages/FavoritesPage'
import PurchasesPage from './pages/PurchasesPage'

import TimelinePage from './pages/TimelinePage'
import IdentityActivationPage from './pages/identity/IdentityActivationPage'
import PublicIdentityPage from './pages/identity/PublicIdentityPage'
import EditIdentityPage from './pages/identity/EditIdentityPage'
import BottomNav from './components/BottomNav'

function App() {
  return (
    <>
      <Toaster position="top-center" />
      <Router>
        <Routes>
          <Route path="/competition/:id" element={<CompetitionPage />} />
          <Route path="/competition/:id/search" element={<SearchPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/payment" element={<PaymentPage />} />
          <Route path="/downloads" element={<DownloadsPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/purchases" element={<PurchasesPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          
          {/* Identity Routes */}
          <Route path="/identity/activate" element={<IdentityActivationPage />} />
          <Route path="/profile/edit" element={<EditIdentityPage />} />
          <Route path="/:handle" element={<PublicIdentityPage />} />
          
          {/* Redirect to a demo competition for MVP testing */}
          <Route path="*" element={<Navigate to="/competition/1" replace />} />
        </Routes>
        <BottomNav />
      </Router>
    </>
  )
}

export default App
