import os

def create_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

def build_checkout():
    base = r"E:\ZoPic Studio\frontend-client\src"
    
    # 1. Update index.css for checkout specific styles
    css_append = """
/* Reveal Animation */
.progressive-reveal {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  background-color: #000;
}

.reveal-watermark {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  object-fit: cover;
  transition: opacity 2s ease-in-out;
}

.reveal-hd {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 2s ease-in-out;
}

.progressive-reveal.revealed .reveal-watermark {
  opacity: 0;
}

.progressive-reveal.revealed .reveal-hd {
  opacity: 1;
}

/* Forms */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--color-text-muted);
}

.form-group input {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background-color: transparent;
  color: #fff;
  font-size: 1rem;
}
"""
    with open(os.path.join(base, "index.css"), 'a', encoding='utf-8') as f:
        f.write(css_append)

    # 2. CheckoutPage
    checkout_page = """import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import { usePaymentStore } from '../store/paymentStore'
import { useDownloadStore } from '../store/downloadStore'
import { ArrowLeft, CheckCircle } from 'lucide-react'

export default function CheckoutPage() {
  const navigate = useNavigate()
  const { items, total, clearCart } = useCartStore()
  const { status, setStatus } = usePaymentStore()
  const { setPurchasedPhotos } = useDownloadStore()
  
  const [phone, setPhone] = useState('')

  const handlePayment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!phone) return

    setStatus('processing')
    // Simulation du paiement Mobile Money
    setTimeout(() => {
      setStatus('success')
      // Transférer le panier vers le store de téléchargement
      setPurchasedPhotos(items.map(i => ({ ...i, hdUrl: i.url + '&hd=true' })))
      clearCart()
      setTimeout(() => navigate('/downloads'), 1500) // Redirige après succès
    }, 3000)
  }

  if (items.length === 0 && status === 'idle') {
    return (
      <div className="container" style={{ textAlign: 'center', marginTop: '4rem' }}>
        <h2>Panier Vide</h2>
        <button className="btn btn-secondary" style={{ marginTop: '2rem' }} onClick={() => navigate(-1)}>
          Retour à la compétition
        </button>
      </div>
    )
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
        <button 
          onClick={() => navigate(-1)} 
          style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>
          <ArrowLeft size={24} />
        </button>
        <h2 style={{ marginLeft: '1rem' }}>Paiement</h2>
      </div>

      {status === 'idle' && (
        <>
          <div className="card">
            <h3>Récapitulatif</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', margin: '1rem 0', color: 'var(--color-text-muted)' }}>
              <span>{items.length} Photo(s)</span>
              <span>{total} FCFA</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '1.2rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
              <span>Total à payer</span>
              <span>{total} FCFA</span>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Mode de Paiement</h3>
            <form onSubmit={handlePayment}>
              <div className="form-group">
                <label>Numéro Wave / Orange Money</label>
                <input 
                  type="tel" 
                  placeholder="Ex: 77 123 45 67" 
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required 
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                Payer {total} FCFA
              </button>
            </form>
          </div>
        </>
      )}

      {status === 'processing' && (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <div style={{ fontSize: '3rem', animation: 'spin 1s linear infinite', marginBottom: '1rem' }}>🔄</div>
          <h3>En attente du paiement...</h3>
          <p style={{ color: 'var(--color-text-muted)' }}>Veuillez valider la transaction sur votre téléphone.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <CheckCircle size={64} style={{ color: 'var(--color-success)', margin: '0 auto 1rem' }} />
          <h3>Paiement Réussi !</h3>
          <p style={{ color: 'var(--color-text-muted)' }}>Génération de vos photos haute définition...</p>
        </div>
      )}
    </div>
  )
}
"""
    create_file(os.path.join(base, "pages", "CheckoutPage.tsx"), checkout_page)

    # 3. DownloadsPage
    downloads_page = """import { useEffect, useState } from 'react'
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
"""
    create_file(os.path.join(base, "pages", "DownloadsPage.tsx"), downloads_page)

if __name__ == "__main__":
    build_checkout()
