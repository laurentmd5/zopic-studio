import { useState } from 'react'
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
