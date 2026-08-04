import { useState, useRef, useEffect } from 'react'
import { Camera, ArrowLeft, Upload, Filter, Check } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useSearchStore } from '../store/searchStore'
import { useCartStore } from '../store/cartStore'

export default function SearchPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const { state, results, setSearchState, setResults } = useSearchStore()
  const { addItem, removeItem, items, total } = useCartStore()

  const videoRef = useRef<HTMLVideoElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [cameraError, setCameraError] = useState(false)
  const [activeTab, setActiveTab] = useState<'toutes' | 'apercus' | 'packs'>('toutes')

  useEffect(() => {
    // Reset state on mount to ensure we start in selfie mode
    if (state !== 'success') {
      setSearchState('idle')
      startCamera()
    }
    return () => stopCamera()
  }, [])

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      setStream(s)
      setCameraError(false)
      if (videoRef.current) {
        videoRef.current.srcObject = s
      }
    } catch (err) {
      console.error("Erreur caméra", err)
      setCameraError(true)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const simulateSearch = () => {
    stopCamera()
    setSearchState('loading')
    setTimeout(() => {
      setSearchState('success')
      setResults([
        { id: 1, url: 'https://images.unsplash.com/photo-1552674605-15c2145b9ce2?w=400&q=80', price: 500 },
        { id: 2, url: 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=400&q=80', price: 500 },
        { id: 3, url: 'https://images.unsplash.com/photo-1571008887538-b36bb32f4571?w=400&q=80', price: 500 },
        { id: 4, url: 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=400&q=80', price: 500 }
      ])
    }, 2500)
  }

  // Écran 2 - Recherche par Selfie
  if (state === 'idle') {
    return (
      <div className="min-h-screen bg-white flex flex-col pb-20">
        <div className="px-6 pt-8 pb-4 flex items-center">
          <button onClick={() => navigate(-1)} className="text-gray-900">
            <ArrowLeft size={24} />
          </button>
          <h2 className="ml-4 text-xl font-bold text-gray-900">Trouver mes photos</h2>
        </div>

        <div className="flex-1 flex flex-col items-center justify-center px-6 -mt-10">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8 max-w-[250px]">
            Prenez un selfie pour trouver vos photos
          </h3>

          <div className="relative mb-8">
            <div className="w-64 h-64 rounded-full overflow-hidden border-4 border-[#3A4B29] bg-gray-100 flex items-center justify-center">
              {cameraError ? (
                <div className="text-center text-gray-500 px-4">
                  <Camera size={48} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Caméra indisponible</p>
                </div>
              ) : (
                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
              )}
            </div>
            {!cameraError && (
              <button 
                onClick={simulateSearch}
                className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-16 h-16 bg-[#3A4B29] rounded-full flex items-center justify-center border-4 border-white shadow-lg"
              >
                <Camera size={24} className="text-white" />
              </button>
            )}
          </div>

          <label className="flex items-center gap-2 text-gray-600 font-medium mt-6 cursor-pointer">
            ou importez une photo
            <Upload size={18} />
            <input type="file" accept="image/*" className="hidden" onChange={simulateSearch} />
          </label>
        </div>
      </div>
    )
  }

  // Loading state
  if (state === 'loading') {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center pb-20">
        <div className="w-16 h-16 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin mb-4"></div>
        <h3 className="text-xl font-bold text-gray-900">Recherche en cours...</h3>
        <p className="text-gray-500 mt-2">Analyse faciale et recherche de vos photos</p>
      </div>
    )
  }

  // Écran 3 - Résultats
  if (state === 'success') {
    return (
      <div className="min-h-screen bg-white pb-32">
        {/* Header */}
        <div className="px-6 pt-8 pb-4 flex items-center justify-between">
          <div className="flex items-center">
            <button onClick={() => setSearchState('idle')} className="text-gray-900">
              <ArrowLeft size={24} />
            </button>
            <h2 className="ml-4 text-xl font-bold text-gray-900">Résultats</h2>
          </div>
          <button className="text-gray-900">
            <Filter size={24} />
          </button>
        </div>

        <div className="px-4">
          {/* Competition Mini Card */}
          <div className="bg-[#3A4B29] rounded-xl p-4 flex items-center gap-4 mb-6 shadow-md text-white">
            <img src="https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=100&q=80" alt="Compétition" className="w-12 h-12 rounded-lg object-cover" />
            <div className="flex-1">
              <h4 className="font-bold">Marathon Dakar 2025</h4>
              <p className="text-xs text-white/80">12 Avril 2025 • Dakar, Sénégal</p>
            </div>
            <div className="text-right">
              <div className="font-bold text-xl">{results.length}</div>
              <div className="text-xs text-white/80">photos</div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200 mb-6">
            <button 
              className={`flex-1 py-3 text-sm font-semibold text-center border-b-2 ${activeTab === 'toutes' ? 'border-[#3A4B29] text-[#3A4B29]' : 'border-transparent text-gray-500'}`}
              onClick={() => setActiveTab('toutes')}
            >
              Toutes ({results.length})
            </button>
            <button 
              className={`flex-1 py-3 text-sm font-semibold text-center border-b-2 ${activeTab === 'apercus' ? 'border-[#3A4B29] text-[#3A4B29]' : 'border-transparent text-gray-500'}`}
              onClick={() => setActiveTab('apercus')}
            >
              Aperçus
            </button>
            <button 
              className={`flex-1 py-3 text-sm font-semibold text-center border-b-2 ${activeTab === 'packs' ? 'border-[#3A4B29] text-[#3A4B29]' : 'border-transparent text-gray-500'}`}
              onClick={() => setActiveTab('packs')}
            >
              Packs
            </button>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-2 gap-3">
            {results.map(photo => {
              const inCart = items.some(i => i.id === photo.id)
              return (
                <div key={photo.id} className="relative cursor-pointer group" onClick={() => inCart ? removeItem(photo.id) : addItem(photo)}>
                  <div className="aspect-square rounded-xl overflow-hidden relative border border-gray-200">
                    <img src={photo.url} alt="Photo" className="w-full h-full object-cover" />
                    {/* Watermark MVP */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <span className="text-white/60 font-black text-xl -rotate-45 tracking-widest drop-shadow-md">ZOPIC</span>
                    </div>
                  </div>
                  
                  {/* Price Label */}
                  <div className="mt-1 flex items-center justify-between">
                    <span className="text-sm font-bold text-gray-900">{photo.price} FCFA</span>
                  </div>

                  {/* Checkbox */}
                  <div className={`absolute top-2 right-2 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${inCart ? 'bg-[#3A4B29] border-[#3A4B29]' : 'bg-black/20 border-white backdrop-blur-sm'}`}>
                    {inCart && <Check size={14} className="text-white" />}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Sticky Bottom Bar */}
        {items.length > 0 && (
          <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 pb-8 flex items-center justify-between z-50 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]" style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 1rem)' }}>
            <div>
              <div className="text-sm font-medium text-gray-600">{items.length} sélectionnée{items.length > 1 ? 's' : ''}</div>
              <div className="text-xl font-bold text-gray-900">{total} FCFA</div>
            </div>
            <button 
              className="px-6 py-3 bg-[#3A4B29] text-white font-bold rounded-xl shadow-md"
              onClick={() => navigate('/checkout')}
            >
              Voir le panier
            </button>
          </div>
        )}
      </div>
    )
  }

}
