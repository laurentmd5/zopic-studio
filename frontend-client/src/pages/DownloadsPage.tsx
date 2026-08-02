import { useEffect, useState } from 'react'
import { useDownloadStore } from '../store/downloadStore'
import { Download } from 'lucide-react'

export default function DownloadsPage() {
  const { purchasedPhotos } = useDownloadStore()
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    // Déclenche l'animation Progressive Reveal après l'arrivée sur la page
    const timer = setTimeout(() => setRevealed(true), 500)
    return () => clearTimeout(timer)
  }, [])

  if (purchasedPhotos.length === 0) {
    return <div className="container">Aucune photo achetée trouvée.</div>
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Vos Photos</h1>
        <p>Merci pour votre achat !</p>
      </div>

      <div className="gallery" style={{ gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        {purchasedPhotos.map(photo => (
          <div key={photo.id} style={{ display: 'flex', flexDirection: 'column' }}>
            <div className={`progressive-reveal ${revealed ? 'revealed' : ''}`} style={{ aspectRatio: '1', width: '100%' }}>
              {/* Image avec filigrane (basse qualité) */}
              <img src={photo.url} className="reveal-watermark" alt="Watermarked" />
              <div className="watermark" style={{ opacity: revealed ? 0 : 1, transition: 'opacity 2s' }}>
                <span>ZOPIC</span>
              </div>
              
              {/* Image HD (Sans filigrane) qui apparaît en fondu */}
              <img src={photo.hdUrl} className="reveal-hd" alt="HD" />
            </div>
            <button className="btn btn-secondary" style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Download size={20} style={{ marginRight: '8px' }} />
              Télécharger HD
            </button>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '3rem', textAlign: 'center' }}>
        <h3>Ne perdez pas vos photos</h3>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem', marginTop: '0.5rem' }}>
          Créez un compte pour sauvegarder cet achat à vie et retrouver vos photos lors de vos prochaines compétitions.
        </p>
        <button className="btn btn-primary">Créer un compte</button>
      </div>
    </div>
  )
}
