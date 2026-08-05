import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import { ChevronLeft, X, ShoppingCart, Lock, Tag } from 'lucide-react'
import './CheckoutPage.css'

export default function CheckoutPage() {
  const navigate = useNavigate()
  const { items, removeItem } = useCartStore()

  if (items.length === 0) {
    return (
      <div className="checkout-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: '80px', height: '80px', backgroundColor: 'var(--color-surface)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
          <Tag size={40} color="var(--color-text-muted)" />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Panier Vide</h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '2rem' }}>Vous n'avez pas encore sélectionné de photos.</p>
        <button className="btn btn-outline" style={{ width: '80%' }} onClick={() => navigate(-1)}>
          Retour aux photos
        </button>
      </div>
    )
  }

  // Calculate pricing based on mockup
  const BASE_PRICE = 590
  const DISCOUNTED_PRICE = 500

  // The mockup shows "Pack 3 photos 1 500 FCFA", which means when they buy 3, they get them for 500 each instead of 590 each.
  // We'll mimic this logic visually.
  const hasPackDiscount = items.length >= 3;
  const originalTotal = items.length * BASE_PRICE;
  const currentTotal = hasPackDiscount ? items.length * DISCOUNTED_PRICE : originalTotal;

  return (
    <div className="checkout-container">
      {/* Header */}
      <header className="checkout-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2 className="page-title">Panier</h2>
        <button className="modifier-btn">Modifier</button>
      </header>

      <div className="checkout-content">
        {/* Event Header */}
        <div className="checkout-event-header">
          <img src="https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=100&q=80" alt="Compétition" className="checkout-event-img" />
          <div>
            <h4 className="checkout-event-title">Marathon Dakar 2025</h4>
            <p className="checkout-event-date">12 Avril 2025 • Dakar, Sénégal</p>
          </div>
        </div>

        {/* Items List */}
        <div className="checkout-items-list">
          {items.map(item => (
            <div key={item.id} className="checkout-item">
              <img src={item.url} alt="Photo" className="checkout-item-img" />
              <div className="checkout-item-info">
                <span className="checkout-item-price">
                  {hasPackDiscount ? DISCOUNTED_PRICE : BASE_PRICE} FCFA
                </span>
                {hasPackDiscount && (
                  <span className="checkout-item-old-price">{BASE_PRICE} FCFA</span>
                )}
              </div>
              <div className="checkout-item-actions">
                <div className="cart-icon-wrapper">
                  <ShoppingCart size={16} />
                </div>
                <button onClick={() => removeItem(item.id)} className="remove-btn">
                  <X size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Discount Block */}
        <div className="offer-block">
          <h3 className="offer-title">Meilleure offre appliquée</h3>
          
          {hasPackDiscount ? (
            <>
              <div className="offer-row active">
                <span>Pack {items.length} photos</span>
                <span>{currentTotal.toLocaleString('fr-FR')} FCFA</span>
              </div>
              <div className="offer-row strikethrough">
                <span>Pack 1 photo</span>
                <span>{originalTotal.toLocaleString('fr-FR')} FCFA</span>
              </div>
            </>
          ) : (
            <div className="offer-row active">
              <span>Pack 1 photo</span>
              <span>{currentTotal.toLocaleString('fr-FR')} FCFA</span>
            </div>
          )}
        </div>

        {/* Total Summary */}
        <div className="total-block">
          <div className="total-label">Total</div>
          <div className="total-value">{currentTotal.toLocaleString('fr-FR')} FCFA</div>
        </div>

      </div>

      {/* Sticky Bottom Bar */}
      <div className="checkout-sticky-bar">
        <button 
          className="checkout-btn"
          onClick={() => navigate('/payment')}
        >
          Procéder au paiement
        </button>
        <div className="secure-payment">
          <Lock size={14} />
          <span>Paiement 100% sécurisé</span>
        </div>
      </div>
    </div>
  )
}
