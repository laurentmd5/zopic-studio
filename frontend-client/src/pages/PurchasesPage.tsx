import { useEffect, useState } from 'react'
import { Download, Package, ArrowRight, MapPin, Calendar } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface OrderItem {
  photo_id: number
}

interface Purchase {
  id: number
  total_amount: number
  created_at: string
  items_count: number
  permission_expires_at: string | null
  archive_status: string | null
  archive_id: number | null
  items: OrderItem[]
  // Mock data for UI
  competition_name: string
  competition_date: string
  competition_location: string
}

export default function PurchasesPage() {
  const navigate = useNavigate()
  const [purchases, setPurchases] = useState<Purchase[]>([])
  const [loading, setLoading] = useState(true)
  const sessionId = "guest-123"

  useEffect(() => {
    const fetchPurchases = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/payments/purchases', {
          headers: { 'X-Session-ID': sessionId }
        })
        
        // Enrich data with mock competition details since the backend might not return them yet
        const enriched = response.data.map((p: any) => ({
          ...p,
          competition_name: "Marathon de Dakar 2026",
          competition_date: new Date(p.created_at).toLocaleDateString(),
          competition_location: "Dakar, Sénégal"
        }))
        
        setPurchases(enriched)
      } catch (error) {
        console.error("Erreur", error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchPurchases()
  }, [sessionId])

  const handleDownloadZip = async (orderId: number) => {
    // API logic simplified for mockup rendering
    setPurchases(prev => prev.map(p => p.id === orderId ? { ...p, archive_status: 'PROCESSING' } : p))
    setTimeout(() => {
      setPurchases(prev => prev.map(p => p.id === orderId ? { ...p, archive_status: 'COMPLETED' } : p))
    }, 2000)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-32">
      {/* Header */}
      <div className="bg-white px-6 pt-8 pb-4 border-b border-gray-100 shadow-sm sticky top-0 z-40">
        <h2 className="text-2xl font-bold text-gray-900">Mes Achats</h2>
      </div>

      <div className="p-4 space-y-6">
        {/* Banner Create Profile */}
        <div className="bg-[#3A4B29] text-white p-4 rounded-xl shadow-md flex items-center justify-between">
          <div>
            <h4 className="font-bold mb-1">Ne perdez pas vos photos</h4>
            <p className="text-xs text-white/80">Créez un compte pour sauvegarder vos achats à vie.</p>
          </div>
          <button 
            onClick={() => navigate('/identity/activate')}
            className="bg-white text-[#3A4B29] px-4 py-2 rounded-lg text-sm font-bold shadow-sm"
          >
            Créer
          </button>
        </div>

        {purchases.length === 0 ? (
          <div className="bg-white p-8 rounded-xl border border-gray-100 flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Package size={28} className="text-gray-400" />
            </div>
            <h3 className="font-bold text-gray-900 mb-2">Aucun achat</h3>
            <p className="text-sm text-gray-500 mb-6">Vos photos achetées apparaîtront ici.</p>
            <button className="btn-outline px-6 py-2 rounded-lg text-sm font-bold" onClick={() => navigate('/')}>
              Découvrir les événements
            </button>
          </div>
        ) : (
          purchases.map(purchase => (
            <div key={purchase.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
              {/* Card Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-gray-900 text-lg">{purchase.competition_name}</h3>
                  <span className="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-1 rounded">
                    {purchase.items_count} photos
                  </span>
                </div>
                
                <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                  <div className="flex items-center gap-1"><Calendar size={14} /> {purchase.competition_date}</div>
                  <div className="flex items-center gap-1"><MapPin size={14} /> {purchase.competition_location}</div>
                </div>

                <button 
                  onClick={() => handleDownloadZip(purchase.id)}
                  disabled={purchase.archive_status === 'PROCESSING'}
                  className={`w-full py-2.5 rounded-lg border-2 font-bold text-sm flex items-center justify-center gap-2 transition-colors
                    ${purchase.archive_status === 'PROCESSING' 
                      ? 'border-gray-200 text-gray-400 bg-gray-50' 
                      : purchase.archive_status === 'COMPLETED'
                        ? 'border-[#3A4B29] text-[#3A4B29] bg-green-50'
                        : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                    }`}
                >
                  <Download size={18} />
                  {purchase.archive_status === 'PROCESSING' 
                    ? 'Préparation de l\'archive...' 
                    : purchase.archive_status === 'COMPLETED'
                      ? 'Télécharger le ZIP'
                      : 'Générer l\'album (ZIP)'}
                </button>
              </div>

              {/* Photos Horizontal Scroll */}
              <div className="p-4 bg-gray-50/50">
                <div className="flex gap-3 overflow-x-auto pb-2 snap-x">
                  {purchase.items.map((item, idx) => (
                    <div key={idx} className="shrink-0 w-24 h-24 rounded-lg bg-gray-200 overflow-hidden snap-start relative border border-gray-200">
                      <img 
                        src={`https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=200&q=80&sig=${item.photo_id}`} 
                        alt="Achetée" 
                        className="w-full h-full object-cover"
                      />
                      <a 
                        href={`http://localhost:8000/api/v1/orders/${purchase.id}/photos/${item.photo_id}/download`}
                        className="absolute bottom-1 right-1 bg-black/50 p-1.5 rounded text-white backdrop-blur-sm"
                        onClick={(e) => e.preventDefault()} // Blocked for demo
                      >
                        <Download size={14} />
                      </a>
                    </div>
                  ))}
                  
                  {/* View All Card */}
                  <div className="shrink-0 w-24 h-24 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-gray-400 snap-start cursor-pointer hover:bg-gray-100 transition-colors">
                    <ArrowRight size={20} className="mb-1" />
                    <span className="text-xs font-medium">Tout voir</span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
