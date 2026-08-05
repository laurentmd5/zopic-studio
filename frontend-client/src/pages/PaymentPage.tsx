import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import { usePaymentStore } from '../store/paymentStore'
import { useDownloadStore } from '../store/downloadStore'
import { useFavoriteStore } from '../store/favoriteStore'
import { ChevronLeft, CheckCircle, Lock, AlertCircle } from 'lucide-react'
import './PaymentPage.css'

type PaymentMethod = 'wave' | 'orange'

export default function PaymentPage() {
  const navigate = useNavigate()
  const { items, clearCart } = useCartStore()
  const { status, setStatus } = usePaymentStore()
  const { setPurchasedPhotos } = useDownloadStore()
  
  const [method, setMethod] = useState<PaymentMethod>('wave')

  // Calculate pricing based on mockup logic
  const BASE_PRICE = 590
  const DISCOUNTED_PRICE = 500
  const hasPackDiscount = items.length >= 3;
  const currentTotal = hasPackDiscount ? items.length * DISCOUNTED_PRICE : items.length * BASE_PRICE;

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
      <div className="payment-container">
        <header className="payment-header">
          <button onClick={() => navigate(-1)} className="back-btn">
            <ChevronLeft size={24} />
          </button>
          <h2 className="page-title">Paiement</h2>
        </header>
        <div className="payment-empty">
          <AlertCircle size={48} color="var(--color-text-muted)" style={{ marginBottom: '1rem' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Aucun paiement en attente</h2>
          <button className="btn btn-outline" style={{ marginTop: '2rem' }} onClick={() => navigate('/')}>
            Retour à l'accueil
          </button>
        </div>
      </div>
    )
  }

  if (status === 'processing') {
    return (
      <div className="payment-container">
        <div className="payment-status">
          <div className="spinner" style={{ marginBottom: '1.5rem', borderColor: 'var(--color-surface)', borderTopColor: 'var(--color-primary)' }}></div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Paiement en cours...</h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Veuillez valider la transaction sur votre application {method === 'wave' ? 'Wave' : 'Orange Money'}.</p>
        </div>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="payment-container">
        <div className="payment-status">
          <CheckCircle size={64} color="var(--color-primary)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Paiement Réussi !</h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Génération de vos photos en haute définition...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="payment-container">
      {/* Header */}
      <header className="payment-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2 className="page-title">Paiement</h2>
      </header>

      <div className="payment-content">
        <div className="amount-block">
          <span className="amount-label">Montant à payer</span>
          <span className="amount-value">{currentTotal.toLocaleString('fr-FR')} FCFA</span>
        </div>

        <div>
          <h3 className="payment-methods-title">Choisissez votre moyen de paiement</h3>
          
          <div className="payment-methods-list">
            {/* Wave */}
            <div 
              onClick={() => setMethod('wave')}
              className={`payment-method-card ${method === 'wave' ? 'active' : ''}`}
            >
              <div className="payment-method-info">
                {/* Wave Logo Placeholder */}
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: '#00B0FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
                  W
                </div>
                <span className="payment-method-name">Wave</span>
              </div>
              <div className="radio-btn">
                <div className="radio-btn-inner"></div>
              </div>
            </div>

            {/* Orange Money */}
            <div 
              onClick={() => setMethod('orange')}
              className={`payment-method-card ${method === 'orange' ? 'active' : ''}`}
            >
              <div className="payment-method-info">
                {/* Orange Money Logo Placeholder */}
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: '#FF6600', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
                  O
                </div>
                <span className="payment-method-name">Orange Money</span>
              </div>
              <div className="radio-btn">
                <div className="radio-btn-inner"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sticky Bottom Bar */}
      <div className="payment-sticky-bar">
        <button 
          className="payment-btn"
          onClick={handlePayment}
        >
          Payer {currentTotal.toLocaleString('fr-FR')} FCFA
        </button>
        <div className="secure-text">
          <Lock size={14} />
          <span>Paiement 100% sécurisé</span>
        </div>
      </div>
    </div>
  )
}
