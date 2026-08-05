import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Search, ShoppingBag, User } from 'lucide-react'

const BottomNav: React.FC = () => {
  const location = useLocation()
  const path = location.pathname

  // Don't show bottom nav on specific pages
  if (path === '/checkout' || path === '/payment' || path === '/identity/activate' || path === '/profile/edit' || path === '/auth') {
    return null
  }

  return (
    <nav className="bottom-nav">
      <Link to="/" className={`bottom-nav-item ${path === '/' ? 'active' : ''}`}>
        <Home size={24} />
        <span>Accueil</span>
      </Link>
      
      <Link to="/competition/1/search" className={`bottom-nav-item ${path.includes('/search') ? 'active' : ''}`}>
        <Search size={24} />
        <span>Recherche</span>
      </Link>
      
      <Link to="/purchases" className={`bottom-nav-item ${path === '/purchases' ? 'active' : ''}`}>
        <ShoppingBag size={24} />
        <span>Achats</span>
      </Link>
      
      <Link to="/dashboard" className={`bottom-nav-item ${path.startsWith('/dashboard') || path.startsWith('/timeline') || path.startsWith('/profile') ? 'active active-profil' : ''}`}>
        <User size={24} />
        <span>Profil</span>
      </Link>
    </nav>
  )
}

export default BottomNav
