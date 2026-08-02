import os

def create_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

def build_ui():
    base = r"E:\ZoPic Studio\frontend-client\src"
    
    # 1. Update index.css for UI elements
    css_append = """
/* UI Elements */
.container {
  max-width: 600px; /* Mobile first optimal width */
  margin: 0 auto;
  padding: 1rem;
}

.card {
  background-color: var(--color-surface);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--color-border);
}

.btn {
  display: block;
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  text-align: center;
  transition: opacity 0.2s;
  color: #fff;
}

.btn:active {
  opacity: 0.8;
}

.btn-primary {
  background-color: var(--color-accent);
}

.btn-secondary {
  background-color: var(--color-border);
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  color: var(--color-accent);
  margin-bottom: 0.5rem;
}

.header p {
  color: var(--color-text-muted);
}

.search-modes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.search-mode-card {
  background-color: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem 1rem;
  text-align: center;
  cursor: pointer;
}

.search-mode-card:hover {
  border-color: var(--color-accent);
}

.search-mode-card svg {
  color: var(--color-accent);
  margin-bottom: 0.5rem;
}

.video-container {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background-color: #000;
  margin-bottom: 1rem;
  aspect-ratio: 3/4;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.photo-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.photo-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.watermark {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.3);
  pointer-events: none;
}

.watermark span {
  color: rgba(255,255,255,0.7);
  font-weight: 900;
  font-size: 1.5rem;
  transform: rotate(-45deg);
  letter-spacing: 5px;
}
"""
    with open(os.path.join(base, "index.css"), 'a', encoding='utf-8') as f:
        f.write(css_append)
        
    # 2. CompetitionPage
    comp_page = """import { useNavigate, useParams } from 'react-router-dom'
import { Calendar, MapPin, Trophy } from 'lucide-react'

export default function CompetitionPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  // Simuler les données récupérées depuis l'API via competitionStore
  const competition = {
    name: "Marathon de Dakar 2026",
    date: "14 Février 2026",
    location: "Corniche Ouest, Dakar",
    sport: "Athlétisme",
    price: "1500 FCFA / photo"
  }

  return (
    <div className="container">
      <div className="header">
        <h1>{competition.name}</h1>
        <p>Revivez vos meilleurs moments sportifs</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Calendar size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.date}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <MapPin size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.location}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Trophy size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.sport}</span>
        </div>
        <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          <p style={{ textAlign: 'center', fontWeight: 'bold' }}>Tarif unique : {competition.price}</p>
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <button className="btn btn-primary" onClick={() => navigate(`/competition/${id}/search`)}>
          🔍 Retrouver mes photos
        </button>
      </div>
    </div>
  )
}
"""
    create_file(os.path.join(base, "pages", "CompetitionPage.tsx"), comp_page)

    # 3. SearchPage
    search_page = """import { useState, useRef } from 'react'
import { Camera, Hash, Users, Image as ImageIcon, ArrowLeft } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useSearchStore } from '../store/searchStore'
import { useCartStore } from '../store/cartStore'

type Mode = 'menu' | 'selfie' | 'dossard' | 'equipe' | 'all'

export default function SearchPage() {
  const navigate = useNavigate()
  const { id } = useParams()
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
"""
    create_file(os.path.join(base, "pages", "SearchPage.tsx"), search_page)

if __name__ == "__main__":
    build_ui()
