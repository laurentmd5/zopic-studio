import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Trophy, 
  FolderOpen, 
  Image as ImageIcon, 
  ShoppingCart, 
  TrendingUp, 
  CreditCard, 
  Settings, 
  HelpCircle,
  Menu,
  Wallet
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'

const DashboardLayout: React.FC = () => {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Tableau de bord', icon: <Home size={20} /> },
    { path: '/competitions', label: 'Compétitions', icon: <Trophy size={20} /> },
    { path: '/albums', label: 'Albums', icon: <FolderOpen size={20} /> },
    { path: '/photos', label: 'Photos', icon: <ImageIcon size={20} /> },
    { path: '/ventes', label: 'Ventes', icon: <ShoppingCart size={20} /> },
    { path: '/revenus', label: 'Revenus', icon: <TrendingUp size={20} /> },
    { path: '/payouts', label: 'Payouts', icon: <Wallet size={20} /> },
    { path: '/abonnements', label: 'Abonnements', icon: <CreditCard size={20} /> },
    { path: '/settings', label: 'Paramètres', icon: <Settings size={20} /> },
    { path: '/aide', label: 'Aide & Support', icon: <HelpCircle size={20} /> },
  ]

  const isActive = (path: string) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex h-screen bg-[#0B1220] overflow-hidden text-slate-300 font-sans">
      
      {/* Sidebar - Fixed Width 260px */}
      <aside className="w-[260px] bg-[#111827] flex flex-col border-r border-slate-800">
        
        {/* Logo */}
        <div className="flex items-center gap-2 p-6">
          <span className="text-3xl font-bold text-[#84CC16]">ZoPic</span>
          <span className="text-xs font-semibold text-[#84CC16] tracking-widest mt-2 uppercase">Studio</span>
        </div>

        {/* User Card */}
        <div className="px-4 mb-6">
          <div className="bg-[#1F2937] rounded-[18px] p-3 flex items-center gap-3 border border-slate-800/50">
            <Avatar className="w-12 h-12">
              <AvatarImage src="https://i.pravatar.cc/150?u=moussa" />
              <AvatarFallback>MF</AvatarFallback>
            </Avatar>
            <div className="flex flex-col">
              <span className="text-slate-100 font-semibold text-sm">Moussa Fall</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Photographe</span>
                <Badge className="bg-[#84CC16] hover:bg-[#65a30d] text-[10px] px-1 py-0 h-4 text-slate-950 font-bold">PRO</Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-1 custom-scrollbar">
          {navItems.map((item) => {
            const active = isActive(item.path)
            return (
              <Link 
                key={item.path} 
                to={item.path} 
                className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 ${
                  active 
                    ? 'bg-[#1e330a] text-[#84CC16]' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {item.icon}
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Storage Widget */}
        <div className="p-4 mt-auto">
          <div className="bg-[#1F2937] rounded-[18px] p-4 border border-slate-800/50">
            <div className="text-xs text-slate-400 mb-2">Stockage utilisé</div>
            <div className="flex justify-between items-end mb-2">
              <div className="text-sm">
                <span className="text-slate-100 font-bold">256 GO</span>
                <span className="text-slate-500"> / 1 TO</span>
              </div>
              <span className="text-xs text-slate-400">25%</span>
            </div>
            <Progress value={25} className="h-2 mb-4 bg-slate-800" />
            <button className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs py-2.5 rounded-xl transition-colors font-medium">
              Gérer mon abonnement
            </button>
          </div>
        </div>

      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden">
        {/* Mobile Header Trigger could go here */}
        <div className="p-8">
          <Outlet />
        </div>
      </main>
      
    </div>
  )
}

export default DashboardLayout
