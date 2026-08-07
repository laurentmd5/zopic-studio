import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Trophy, 
  FolderOpen, 
  Image as ImageIcon, 
  ShoppingCart, 
  ArrowDownToLine,
  Bell,
  ChevronDown,
  Download,
  CreditCard,
  CheckCircle2
} from 'lucide-react'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'

// Mock Data for Charts
const revenueData = [
  { date: '14 Avr', amount: 200000 },
  { date: '16 Avr', amount: 220000 },
  { date: '18 Avr', amount: 280000 },
  { date: '20 Avr', amount: 210000 },
  { date: '22 Avr', amount: 480000 },
  { date: '24 Avr', amount: 290000 },
  { date: '26 Avr', amount: 200000 },
  { date: '28 Avr', amount: 350000 },
  { date: '30 Avr', amount: 520000 },
  { date: '2 Mai', amount: 300000 },
  { date: '4 Mai', amount: 480000 },
  { date: '6 Mai', amount: 310000 },
  { date: '8 Mai', amount: 450000 },
  { date: '10 Mai', amount: 400000 },
  { date: '12 Mai', amount: 650000 },
]

const storageData = [
  { name: 'Photos originales', value: 180, color: '#4ade80' },
  { name: 'Aperçus & miniatures', value: 56, color: '#3b82f6' },
  { name: 'Autres fichiers', value: 20, color: '#f59e0b' },
]

const recentActivities = [
  { id: 1, type: 'sale', title: 'Nouvelle vente - Pack 3 photos', subtitle: 'Marathon Dakar 2025', time: 'il y a 2 min', amount: '7 500 FCFA', icon: <Download size={16} className="text-green-500" /> },
  { id: 2, type: 'payment', title: 'Paiement reçu', subtitle: 'Tournoi Navétanes Ouakam', time: 'il y a 15 min', amount: '12 000 FCFA', icon: <CreditCard size={16} className="text-orange-400" /> },
  { id: 3, type: 'upload', title: 'Nouvelle photo uploadée', subtitle: 'Ligue 1 Sénégal - J20', time: 'il y a 1 h', amount: '—', icon: <ImageIcon size={16} className="text-blue-500" /> },
  { id: 4, type: 'payout', title: 'Demande de payout approuvée', subtitle: '', time: 'il y a 2 h', amount: '350 000 FCFA', icon: <CheckCircle2 size={16} className="text-green-500" /> },
]

const salesByCompetition = [
  { id: 1, name: 'Marathon Dakar 2025', amount: '532 000 FCFA', percent: '42%', color: 'bg-green-500' },
  { id: 2, name: 'Tournoi Navétanes Ouakam', amount: '312 000 FCFA', percent: '25%', color: 'bg-orange-500' },
  { id: 3, name: 'Ligue 1 Sénégal - J20', amount: '245 000 FCFA', percent: '19%', color: 'bg-blue-500' },
  { id: 4, name: 'Semi-Marathon Saint-Louis', amount: '156 000 FCFA', percent: '12%', color: 'bg-yellow-500' },
]

const Dashboard: React.FC = () => {
  return (
    <div className="flex flex-col gap-8 pb-12 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-1">Bonjour Moussa 👋</h1>
          <p className="text-slate-400">Voici un aperçu de votre activité sur ZoPic Studio.</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-[#1F2937] px-3 py-2 rounded-xl border border-slate-800 cursor-pointer">
            <span className="text-xs text-slate-400">Période</span>
            <span className="text-sm text-slate-200">30 derniers jours</span>
            <ChevronDown size={16} className="text-slate-400" />
          </div>
          
          <button className="relative bg-[#1F2937] p-2.5 rounded-xl border border-slate-800 hover:bg-slate-800 transition-colors">
            <Bell size={20} className="text-slate-300" />
            <span className="absolute top-1.5 right-2 w-2 h-2 bg-red-500 rounded-full animate-bounce"></span>
          </button>
          
          <Button className="bg-[#84CC16] hover:bg-[#65a30d] text-[#0B1220] font-semibold rounded-xl h-10 px-4">
            + Nouvelle compétition
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[
          { title: 'Compétitions', value: '12', trend: '+2 ce mois', icon: <Trophy size={20} className="text-orange-400" /> },
          { title: 'Albums', value: '28', trend: '+7 ce mois', icon: <FolderOpen size={20} className="text-yellow-400" /> },
          { title: 'Photos uploadées', value: '3 486', trend: '+1 248 ce mois', icon: <ImageIcon size={20} className="text-blue-400" /> },
          { title: 'Photos vendues', value: '1 248', trend: '+18% ce mois', icon: <ShoppingCart size={20} className="text-green-400" /> },
          { title: 'Revenus', value: '1 245 000 FCFA', trend: '+22% ce mois', icon: <ArrowDownToLine size={20} className="text-[#84CC16]" /> },
        ].map((kpi, index) => (
          <Card key={index} className="bg-[#1F2937] border-slate-800/50 rounded-[18px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2 pt-4 px-5">
              <CardTitle className="text-sm font-medium text-slate-300">{kpi.title}</CardTitle>
              <div className="bg-[#0B1220]/50 p-2 rounded-lg border border-slate-800">
                {kpi.icon}
              </div>
            </CardHeader>
            <CardContent className="px-5 pb-4">
              <div className="text-2xl font-bold text-slate-100">{kpi.value}</div>
              <p className="text-xs text-[#84CC16] mt-1 font-medium">{kpi.trend}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Area Chart */}
        <Card className="lg:col-span-2 bg-[#1F2937] border-slate-800/50 rounded-[18px]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold text-slate-100">Revenus</CardTitle>
            <div className="flex items-center gap-2 bg-[#0B1220] px-3 py-1.5 rounded-lg border border-slate-800 text-xs text-slate-300 cursor-pointer">
              30 derniers jours <ChevronDown size={14} />
            </div>
          </CardHeader>
          <CardContent className="h-[300px] mt-4 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#84CC16" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#84CC16" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.5} />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  tickFormatter={(value) => `${value >= 1000 ? value / 1000 + 'K' : value}`}
                  dx={-10}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                  itemStyle={{ color: '#84CC16', fontWeight: 'bold' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="amount" 
                  stroke="#84CC16" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorRevenue)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Sales by Competition */}
        <Card className="bg-[#1F2937] border-slate-800/50 rounded-[18px]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-100">Ventes par compétition</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            {salesByCompetition.map((sale) => (
              <div key={sale.id} className="flex items-center justify-between cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-sm ${sale.color}`}></div>
                  <span className="text-sm text-slate-300 group-hover:text-slate-100 transition-colors">{sale.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-slate-200">{sale.amount}</span>
                  <span className="text-sm text-slate-400 w-8 text-right">{sale.percent}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recent Activity */}
        <Card className="lg:col-span-2 bg-[#1F2937] border-slate-800/50 rounded-[18px]">
          <CardHeader className="flex flex-row items-center gap-4 pb-4 border-b border-slate-800/50">
            <CardTitle className="text-lg font-semibold text-slate-100">Périodement</CardTitle>
            <CardTitle className="text-lg font-semibold text-slate-400">Activité récente</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="flex flex-col gap-6">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-4">
                  <div className="mt-1 w-24 text-xs text-slate-400 hidden sm:block">
                    {activity.time}
                  </div>
                  <div className="bg-[#0B1220] p-2 rounded-lg border border-slate-800">
                    {activity.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{activity.title}</p>
                        {activity.subtitle && (
                          <p className="text-xs text-slate-500 mt-0.5">{activity.subtitle}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-slate-200">{activity.amount}</p>
                        <p className="text-xs text-slate-400 mt-0.5 sm:hidden">{activity.time}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Storage */}
        <Card className="bg-[#1F2937] border-slate-800/50 rounded-[18px]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-100">Stockage</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="relative w-32 h-32 flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={storageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={60}
                    stroke="none"
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {storageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-lg font-bold text-slate-100">256 go</span>
                <span className="text-[10px] text-slate-400">Utilisés</span>
              </div>
            </div>

            <div className="flex-1 flex flex-col gap-3 w-full">
              {storageData.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: item.color }}></div>
                    <span className="text-slate-300">{item.name}</span>
                  </div>
                  <span className="text-slate-400 font-medium">{item.value} GO</span>
                </div>
              ))}
              <div className="flex items-center justify-between text-xs pt-3 border-t border-slate-800/50 mt-1">
                <span className="text-slate-200 font-semibold">Total</span>
                <span className="text-slate-200 font-semibold">1 TO</span>
              </div>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}

export default Dashboard
