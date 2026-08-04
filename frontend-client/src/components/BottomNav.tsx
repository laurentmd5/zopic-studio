import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Search, ShoppingBag, User } from 'lucide-react'

const BottomNav: React.FC = () => {
  const location = useLocation()
  
  const navItems = [
    { path: '/competition/1', icon: <Home size={24} />, label: 'Accueil' },
    { path: '/competition/1/search', icon: <Search size={24} />, label: 'Recherche' },
    { path: '/purchases', icon: <ShoppingBag size={24} />, label: 'Achats' },
    { path: '/identity/activate', icon: <User size={24} />, label: 'Profil' },
  ]

  // Hide BottomNav on public identity page
  if (location.pathname.startsWith('/@')) {
    return null
  }

  return (
    <div className="bottom-nav">
      {navItems.map((item) => (
        <Link 
          key={item.label} 
          to={item.path} 
          className={`bottom-nav-item ${location.pathname === item.path ? 'active' : ''}`}
        >
          {item.icon}
          <span>{item.label}</span>
        </Link>
      ))}
    </div>
  )
}

export default BottomNav
