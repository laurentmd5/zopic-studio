import { useState, useRef, useEffect } from 'react'
import { Camera, ChevronLeft, Upload, Check, Filter } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useSearchStore } from '../store/searchStore'
import { useCartStore } from '../store/cartStore'
import './SearchPage.css'

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

  const handleCapture = async () => {
    if (!consent) return;
    const compId = id || '1';
    let fileToUpload: Blob | null = null;
    
    if (videoRef.current && stream) {
       const canvas = document.createElement('canvas');
       canvas.width = videoRef.current.videoWidth;
       canvas.height = videoRef.current.videoHeight;
       const ctx = canvas.getContext('2d');
       if (ctx) {
         ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
         fileToUpload = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
       }
    }

    if (!fileToUpload) {
       alert("Erreur de capture de l'image");
       return;
    }
    
    await performSearch(fileToUpload, compId);
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!consent) return;
    const file = e.target.files?.[0];
    if (file) {
      const compId = id || '1';
      performSearch(file, compId);
    }
  }

  const performSearch = async (file: Blob | File, compId: string) => {
    stopCamera();
    setSearchState('loading');
    try {
      const formData = new FormData();
      formData.append('file', file, 'selfie.jpg');
      formData.append('competition_id', compId);
      formData.append('consent', consent ? 'true' : 'false');

      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const token = localStorage.getItem('token');
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(`${API_URL}/faces/search`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 403) {
            throw new Error("Le consentement biométrique est obligatoire.");
        }
        throw new Error("Erreur IA ou serveur (Code: " + response.status + ")");
      }

      const data = await response.json();
      
      const searchResults = (data.results || []).map((r: any) => ({
         id: r.photo_id || Math.random(),
         url: r.url || 'https://images.unsplash.com/photo-1552674605-15c2145b9ce2?w=400&q=80',
         price: r.price_xof || 500,
      }));

      setResults(searchResults);
      setSearchState('success');
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Erreur lors de la recherche");
      setSearchState('idle');
      startCamera();
    }
  }

  const [consent, setConsent] = useState(false)

  // Écran 2 - Recherche par Selfie
  if (state === 'idle') {
    return (
      <div className="search-page-container">
        <header className="page-header">
          <button onClick={() => navigate(-1)} className="back-btn">
            <ChevronLeft size={24} />
          </button>
          <h2 className="page-title">Trouver mes photos</h2>
        </header>

        <section className="selfie-section">
          <h3 className="selfie-title">
            Prenez un selfie<br />pour trouver vos photos
          </h3>

          <div className="camera-container">
            <div className="camera-circle">
              {cameraError ? (
                <div className="camera-error">
                  <Camera size={48} style={{ opacity: 0.5, marginBottom: '8px' }} />
                  <p>Caméra indisponible</p>
                </div>
              ) : (
                <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
              )}
            </div>

            <div className="consent-container" style={{ margin: '16px', textAlign: 'left', fontSize: '0.85rem' }}>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', cursor: 'pointer' }}>
                <input 
                  type="checkbox" 
                  checked={consent}
                  onChange={(e) => setConsent(e.target.checked)}
                  style={{ marginTop: '4px' }}
                />
                <span style={{ color: 'var(--text-secondary)' }}>
                  J'accepte que mon visage soit analysé temporairement pour retrouver mes photos. Aucune image de mon visage n'est conservée. <a href="/privacy" style={{ color: 'var(--primary-color)', textDecoration: 'underline' }}>Politique de confidentialité</a>
                </span>
              </label>
            </div>

            {!cameraError && (
              <button 
                onClick={handleCapture} 
                className="capture-btn"
                disabled={!consent}
                style={{ opacity: consent ? 1 : 0.5, cursor: consent ? 'pointer' : 'not-allowed' }}
              >
                <Camera size={24} />
              </button>
            )}
          </div>

          <label className="import-section" style={{ opacity: consent ? 1 : 0.5, cursor: consent ? 'pointer' : 'not-allowed' }}>
            <span className="import-text">ou importez une photo</span>
            <div className="import-icon-wrapper">
              <Upload size={20} />
            </div>
            <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} disabled={!consent} />
          </label>
        </section>
      </div>
    )
  }

  // Loading state
  if (state === 'loading') {
    return (
      <div className="search-page-container">
        <div className="loading-section">
          <div className="spinner"></div>
          <h3 className="loading-title">Recherche en cours...</h3>
          <p className="loading-subtitle">Analyse faciale et recherche de vos photos</p>
        </div>
      </div>
    )
  }

  // Écran 3 - Résultats
  if (state === 'success') {
    return (
      <div className="search-page-container">
        {/* Header */}
        <header className="page-header">
          <button onClick={() => setSearchState('idle')} className="back-btn">
            <ChevronLeft size={24} />
          </button>
          <h2 className="page-title">Résultats</h2>
          <button className="page-actions">
            <Filter size={24} />
          </button>
        </header>

        <div className="results-container">
          {/* Competition Mini Card */}
          <div className="event-card">
            <img src="https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=100&q=80" alt="Compétition" className="event-card-img" />
            <div className="event-card-info">
              <h4 className="event-card-title">Marathon Dakar 2025</h4>
              <p className="event-card-date">12 Avril 2025 • Dakar, Sénégal</p>
            </div>
            <div className="event-card-stats">
              <div className="count">{results.length}</div>
              <div className="label">photos</div>
            </div>
          </div>

          {/* Tabs */}
          <div className="tabs-container">
            <button 
              className={`tab ${activeTab === 'toutes' ? 'active' : ''}`}
              onClick={() => setActiveTab('toutes')}
            >
              Toutes ({results.length})
            </button>
            <button 
              className={`tab ${activeTab === 'apercus' ? 'active' : ''}`}
              onClick={() => setActiveTab('apercus')}
            >
              Aperçus
            </button>
            <button 
              className={`tab ${activeTab === 'packs' ? 'active' : ''}`}
              onClick={() => setActiveTab('packs')}
            >
              Packs
            </button>
          </div>

          {/* Grid */}
          <div className="photo-grid">
            {results.map(photo => {
              const inCart = items.some(i => i.id === photo.id)
              return (
                <div key={photo.id} className="photo-item" onClick={() => inCart ? removeItem(photo.id) : addItem(photo)}>
                  <div className="photo-image-wrapper">
                    <img src={photo.url} alt="Photo" className="photo-img" />
                    
                    {/* Repeated text watermark simulation */}
                    <div className="photo-watermark-overlay">
                      <span className="photo-watermark-text">{photo.price} FCFA</span>
                      <span className="photo-watermark-text">{photo.price} FCFA</span>
                      <span className="photo-watermark-text">{photo.price} FCFA</span>
                    </div>
                    
                    {/* Top right indicator: Either the Checkbox or the Price Badge */}
                    {inCart ? (
                      <div className="photo-checkbox">
                        <Check size={14} />
                      </div>
                    ) : (
                      <div className="photo-price-badge">
                        {photo.price} FCFA
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Sticky Bottom Bar */}
        {items.length > 0 && (
          <div className="sticky-action-bar">
            <div className="sticky-action-info">
              <div className="count">{items.length} sélectionnée{items.length > 1 ? 's' : ''}</div>
              <div className="total">{total.toLocaleString('fr-FR')} FCFA</div>
            </div>
            <button 
              className="btn-sticky"
              onClick={() => navigate('/checkout')}
            >
              Voir le panier
            </button>
          </div>
        )}
      </div>
    )
  }

  return null
}
