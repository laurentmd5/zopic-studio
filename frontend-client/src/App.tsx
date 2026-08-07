import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import CompetitionPage from './pages/CompetitionPage'
import SearchPage from './pages/SearchPage'
import CheckoutPage from './pages/CheckoutPage'
import PaymentPage from './pages/PaymentPage'
import PurchasesPage from './pages/PurchasesPage'
import DashboardPage from './pages/DashboardPage'
import TimelinePage from './pages/TimelinePage'
import IdentityActivationPage from './pages/identity/IdentityActivationPage'
import PublicIdentityPage from './pages/identity/PublicIdentityPage'
import EditIdentityPage from './pages/identity/EditIdentityPage'
import GalleryPage from './pages/identity/GalleryPage'
import SharesPage from './pages/identity/SharesPage'
import AuthPage from './pages/identity/AuthPage'
import BottomNav from './components/BottomNav'
import HomePage from './pages/HomePage'
import { AuthProvider } from './context/AuthContext'

function AppLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isPublicProfile = location.pathname.startsWith('/@');

  if (isPublicProfile) {
    // Rend la page sur toute la largeur de l'écran
    return <div style={{ width: '100%', minHeight: '100vh' }}>{children}</div>;
  }

  // Rend l'application avec le format téléphone (430px)
  return (
    <div className="app-container">
      {children}
      <BottomNav />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-center" />
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/search" element={<SearchPage />} />
            
            {/* Competitions */}
            <Route path="/competition/:id" element={<CompetitionPage />} />
            <Route path="/competition/:id/search" element={<SearchPage />} />
            
            {/* E-commerce */}
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/payment" element={<PaymentPage />} />
            <Route path="/purchases" element={<PurchasesPage />} />
            
            {/* Dashboard & Profile */}
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/timeline" element={<TimelinePage />} />

            {/* Identity Routes */}
            <Route path="/identity/activate" element={<IdentityActivationPage />} />
            <Route path="/profile/edit" element={<EditIdentityPage />} />
            <Route path="/profile/gallery" element={<GalleryPage />} />
            <Route path="/profile/shares" element={<SharesPage />} />
            <Route path="/:handle" element={<PublicIdentityPage />} />
          </Routes>
        </AppLayout>
      </Router>
    </AuthProvider>
  )
}

export default App
