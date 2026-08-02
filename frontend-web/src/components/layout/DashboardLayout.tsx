import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Camera, LayoutDashboard, FolderOpen, CreditCard, Settings, LogOut, Moon, Sun, Wallet } from 'lucide-react'
import { useThemeStore } from '../../store/useThemeStore'
import { useAuthStore } from '../../store/useAuthStore'
import styles from './DashboardLayout.module.css'

const DashboardLayout: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore()
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Tableau de bord', icon: <LayoutDashboard size={20} /> },
    { path: '/competitions', label: 'Compétitions', icon: <FolderOpen size={20} /> },
    { path: '/payouts', label: 'Portefeuille', icon: <Wallet size={20} /> },
    { path: '/billing', label: 'Abonnements', icon: <CreditCard size={20} /> },
    { path: '/settings', label: 'Paramètres', icon: <Settings size={20} /> },
  ]

  // Determine page title based on route
  const getPageTitle = () => {
    if (location.pathname.startsWith('/competitions')) return 'Compétitions'
    if (location.pathname.startsWith('/billing')) return 'Abonnements'
    if (location.pathname.startsWith('/settings')) return 'Paramètres'
    if (location.pathname.startsWith('/payouts')) return 'Rétrocessions'
    return 'Tableau de bord'
  }

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.logo}>
            <Camera size={28} />
          </div>
          <h2>ZoPic Studio</h2>
        </div>

        <nav className={styles.nav}>
          {navItems.map((item) => (
            <Link 
              key={item.path} 
              to={item.path} 
              className={`${styles.navItem} ${location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path)) ? styles.active : ''}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <button className={styles.themeToggle} onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            <span>{theme === 'light' ? 'Mode Sombre' : 'Mode Clair'}</span>
          </button>
          
          <button className={styles.logoutBtn} onClick={() => {
            useAuthStore.getState().logout()
            window.location.href = '/login'
          }}>
            <LogOut size={20} />
            <span>Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className={styles.mainContent}>
        <header className={styles.header}>
          <h1>{getPageTitle()}</h1>
          <div className={styles.userProfile}>
            <div className={styles.avatar}>P</div>
          </div>
        </header>
        
        <div className={styles.content}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default DashboardLayout
