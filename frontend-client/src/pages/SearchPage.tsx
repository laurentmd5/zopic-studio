import { useState, useRef } from 'react'
import { Camera, Hash, Users, Image as ImageIcon, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useSearchStore } from '../store/searchStore'
import { useCartStore } from '../store/cartStore'

type Mode = 'menu' | 'selfie' | 'dossard' | 'equipe' | 'all'

export default function SearchPage() {
  const navigate = useNavigate()
  // const { id } = useParams() // Removed unused variable
  const [mode, setMode] = useState<Mode>('menu')
  const { state, results, setSearchState, setResults } = useSearchStore()
  const { addItem, items } = useCartStore()

  const videoRef = useRef<HTMLVideoElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      setStream(s)
      if (videoRef.current) {
        videoRef.current.srcObject = s
      }
    } catch (err) {
      console.error("Erreur caméra", err)
      // Fallback géré implicitement par le bouton upload
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
        { id: 1, url: 'https://images.unsplash.com/photo-1552674605-15c2145b9ce2?w=400&q=80', price: 1500 },
        { id: 2, url: 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=400&q=80', price: 1500 },
        { id: 3, url: 'https://images.unsplash.com/photo-1571008887538-b36bb32f4571?w=400&q=80', price: 1500 }
      ])
    }, 2500)
  }

  const handleSelfieSelect = () => {
    setMode('selfie')
    setSearchState('idle')
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
        <button 
          onClick={() => mode === 'menu' ? navigate(-1) : setMode('menu')} 
          style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>
          <ArrowLeft size={24} />
        </button>
        <h2 style={{ marginLeft: '1rem' }}>Recherche</h2>
      </div>

      {mode === 'menu' && (
        <div className="search-modes">
          <div className="search-mode-card" onClick={handleSelfieSelect}>
            <Camera size={32} />
            <h3>Selfie</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Le plus rapide</p>
          </div>
          <div className="search-mode-card" onClick={() => setMode('dossard')}>
            <Hash size={32} />
            <h3>Dossard</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>N° participant</p>
          </div>
          <div className="search-mode-card" onClick={() => setMode('equipe')}>
            <Users size={32} />
            <h3>Équipe</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Nom de l'équipe</p>
          </div>
          <div className="search-mode-card" onClick={() => simulateSearch()}>
            <ImageIcon size={32} />
            <h3>Tout</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Parcourir</p>
          </div>
        </div>
      )}

      {mode === 'selfie' && state === 'idle' && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem', textAlign: 'center' }}>Retrouvez-vous par l'IA</h3>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem', textAlign: 'center' }}>
            Nous allons analyser votre visage pour retrouver vos photos instantanément. Aucune photo n'est conservée après la recherche.
          </p>
          
          {!stream && (
            <button className="btn btn-primary" onClick={startCamera} style={{ marginBottom: '1rem' }}>
              📸 Autoriser la caméra
            </button>
          )}

          {stream && (
            <>
              <div className="video-container">
                <video ref={videoRef} autoPlay playsInline muted />
              </div>
              <button className="btn btn-primary" onClick={simulateSearch} style={{ marginBottom: '1rem' }}>
                Prendre la photo et rechercher
              </button>
            </>
          )}

          <div style={{ textAlign: 'center' }}>
             <p style={{ color: 'var(--color-text-muted)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Ou</p>
             <label className="btn btn-secondary" style={{ display: 'block', cursor: 'pointer' }}>
               📂 Choisir une photo
               <input type="file" accept="image/*" style={{ display: 'none' }} onChange={simulateSearch} />
             </label>
          </div>
        </div>
      )}

      {state === 'loading' && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div className="spinner" style={{ fontSize: '3rem', animation: 'spin 1s linear infinite', marginBottom: '1rem' }}>🤖</div>
          <h3>Analyse IA en cours...</h3>
          <p style={{ color: 'var(--color-text-muted)' }}>Recherche de votre visage parmi des milliers de photos.</p>
        </div>
      )}

      {state === 'success' && (
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Résultats ({results.length})</h3>
          <div className="gallery">
            {results.map(photo => {
              const inCart = items.some(i => i.id === photo.id)
              return (
                <div key={photo.id} className="photo-card" onClick={() => !inCart && addItem(photo)}>
                  <img src={photo.url} alt="Sport" />
                  <div className="watermark"><span>ZOPIC</span></div>
                  {inCart && (
                    <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(3,218,198,0.3)', border: '2px solid var(--color-success)', borderRadius: '8px' }}></div>
                  )}
                </div>
              )
            })}
          </div>
          
          {items.length > 0 && (
            <div style={{ position: 'fixed', bottom: '1rem', left: '1rem', right: '1rem' }}>
               <button className="btn btn-primary" onClick={() => navigate('/checkout')}>
                 Panier ({items.length}) - {items.length * 1500} FCFA ➡️
               </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
