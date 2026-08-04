import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import { ArrowLeft, Trash2, Tag } from 'lucide-react'

export default function CheckoutPage() {
  const navigate = useNavigate()
  const { items, total, savings, removeItem } = useCartStore()

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center pb-20 px-6">
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Tag size={32} className="text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Panier Vide</h2>
        <p className="text-gray-500 text-center mb-8">Vous n'avez pas encore sélectionné de photos.</p>
        <button className="btn-outline w-full py-4 font-bold rounded-xl" onClick={() => navigate(-1)}>
          Retour aux photos
        </button>
      </div>
    )
  }

  // Original price without packs
  const originalPrice = items.reduce((sum, item) => sum + (item.price || 1500), 0)

  return (
    <div className="min-h-screen bg-white pb-32">
      {/* Header */}
      <div className="px-6 pt-8 pb-4 flex items-center justify-between border-b border-gray-100">
        <div className="flex items-center">
          <button onClick={() => navigate(-1)} className="text-gray-900">
            <ArrowLeft size={24} />
          </button>
          <h2 className="ml-4 text-xl font-bold text-gray-900">Panier</h2>
        </div>
        <button className="text-gray-500 text-sm font-medium">Modifier</button>
      </div>

      <div className="px-4 pt-4">
        {/* Items List */}
        <div className="space-y-4 mb-8">
          {items.map(item => (
            <div key={item.id} className="flex items-center gap-4 bg-white p-2 rounded-xl border border-gray-100 shadow-sm">
              <img src={item.url} alt="Photo" className="w-16 h-16 rounded-lg object-cover" />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${savings > 0 ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
                    {item.price || 1500} FCFA
                  </span>
                  {savings > 0 && <span className="badge">Pack</span>}
                </div>
              </div>
              <button onClick={() => removeItem(item.id)} className="p-2 text-gray-400 hover:text-red-500">
                <Trash2 size={20} />
              </button>
            </div>
          ))}
        </div>

        {/* Discount Block */}
        {savings > 0 && (
          <div className="bg-[#E8F5E9] rounded-xl p-4 mb-8">
            <div className="text-sm text-[#3A4B29] font-medium mb-1">Meilleure offre appliquée</div>
            <div className="flex justify-between items-center">
              <div className="font-bold text-[#3A4B29]">Pack {items.length} photos</div>
              <div className="text-right">
                <div className="text-sm text-gray-500 line-through">{originalPrice} FCFA</div>
                <div className="font-bold text-[#3A4B29]">{total} FCFA</div>
              </div>
            </div>
          </div>
        )}

        {/* Total Summary */}
        <div className="flex justify-between items-end mb-6">
          <div className="text-gray-500 font-medium">Total</div>
          <div className="text-3xl font-black text-gray-900">{total} FCFA</div>
        </div>

      </div>

      {/* Sticky Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 pb-8 z-50 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]" style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 1rem)' }}>
        <button 
          className="w-full py-4 bg-[#3A4B29] text-white font-bold rounded-xl shadow-md text-lg"
          onClick={() => navigate('/payment')}
        >
          Procéder au paiement
        </button>
      </div>
    </div>
  )
}
