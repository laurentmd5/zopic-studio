import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import { usePaymentStore } from '../store/paymentStore'
import { useDownloadStore } from '../store/downloadStore'
import { useFavoriteStore } from '../store/favoriteStore'
import { ArrowLeft, CheckCircle, Lock } from 'lucide-react'

type PaymentMethod = 'wave' | 'orange' | 'card'

export default function PaymentPage() {
  const navigate = useNavigate()
  const { items, total, clearCart } = useCartStore()
  const { status, setStatus } = usePaymentStore()
  const { setPurchasedPhotos } = useDownloadStore()
  
  const [method, setMethod] = useState<PaymentMethod>('wave')

  const handlePayment = () => {
    if (items.length === 0) return

    setStatus('processing')
    // Simulation du paiement
    setTimeout(() => {
      setStatus('success')
      // Transférer le panier vers le store de téléchargement
      setPurchasedPhotos(items.map(i => ({ ...i, hdUrl: i.url + '&hd=true' })))
      
      // Retirer les photos achetées des favoris
      const { removeFavorites } = useFavoriteStore.getState()
      removeFavorites(items.map(i => i.id))
      
      clearCart()
      setTimeout(() => navigate('/purchases'), 1500) // Redirige après succès
    }, 2000)
  }

  // Si on accède directement sans panier, on redirige
  if (items.length === 0 && status === 'idle') {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6">
        <h2 className="text-xl font-bold mb-4">Aucun paiement en attente</h2>
        <button className="btn-outline w-full py-4 rounded-xl" onClick={() => navigate('/')}>Retour à l'accueil</button>
      </div>
    )
  }

  if (status === 'processing') {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 pb-20">
        <div className="w-16 h-16 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin mb-4"></div>
        <h3 className="text-xl font-bold text-gray-900">Paiement en cours...</h3>
        <p className="text-gray-500 mt-2 text-center">Veuillez valider la transaction sur votre application de paiement.</p>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 pb-20">
        <CheckCircle size={64} className="text-[#3A4B29] mb-4" />
        <h3 className="text-2xl font-bold text-gray-900">Paiement Réussi !</h3>
        <p className="text-gray-500 mt-2 text-center">Génération de vos photos en haute définition...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white pb-40">
      {/* Header */}
      <div className="px-6 pt-8 pb-4 flex items-center border-b border-gray-100">
        <button onClick={() => navigate(-1)} className="text-gray-900">
          <ArrowLeft size={24} />
        </button>
        <h2 className="ml-4 text-xl font-bold text-gray-900">Paiement</h2>
      </div>

      <div className="px-6 pt-8">
        <div className="text-sm font-medium text-gray-500 mb-2">Montant à payer</div>
        <div className="text-4xl font-black text-gray-900 mb-8">{total} FCFA</div>

        <h3 className="font-semibold text-gray-900 mb-4">Choisissez votre moyen de paiement</h3>
        
        <div className="space-y-3">
          {/* Wave */}
          <div 
            onClick={() => setMethod('wave')}
            className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-colors ${method === 'wave' ? 'border-[#3A4B29] bg-green-50/50' : 'border-gray-100 bg-white'}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold text-xl">~</div>
              <span className="font-semibold text-gray-900">Wave</span>
            </div>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${method === 'wave' ? 'border-[#3A4B29]' : 'border-gray-300'}`}>
              {method === 'wave' && <div className="w-3 h-3 bg-[#3A4B29] rounded-full"></div>}
            </div>
          </div>

          {/* Orange Money */}
          <div 
            onClick={() => setMethod('orange')}
            className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-colors ${method === 'orange' ? 'border-[#3A4B29] bg-green-50/50' : 'border-gray-100 bg-white'}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center text-white font-bold">OM</div>
              <span className="font-semibold text-gray-900">Orange Money</span>
            </div>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${method === 'orange' ? 'border-[#3A4B29]' : 'border-gray-300'}`}>
              {method === 'orange' && <div className="w-3 h-3 bg-[#3A4B29] rounded-full"></div>}
            </div>
          </div>

          {/* Carte Bancaire */}
          <div 
            onClick={() => setMethod('card')}
            className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-colors ${method === 'card' ? 'border-[#3A4B29] bg-green-50/50' : 'border-gray-100 bg-white'}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center text-white font-bold text-xs">CB</div>
              <span className="font-semibold text-gray-900">Carte bancaire</span>
            </div>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${method === 'card' ? 'border-[#3A4B29]' : 'border-gray-300'}`}>
              {method === 'card' && <div className="w-3 h-3 bg-[#3A4B29] rounded-full"></div>}
            </div>
          </div>
        </div>
      </div>

      {/* Sticky Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white p-4 pb-8 z-50 flex flex-col items-center gap-3 shadow-[0_-10px_20px_rgba(0,0,0,0.02)]" style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 1rem)' }}>
        <button 
          className="w-full py-4 bg-[#3A4B29] text-white font-bold rounded-xl shadow-md text-lg"
          onClick={handlePayment}
        >
          Payer {total} FCFA
        </button>
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <Lock size={14} />
          Paiement 100% sécurisé
        </div>
      </div>
    </div>
  )
}
