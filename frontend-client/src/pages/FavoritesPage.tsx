import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Heart, Search } from 'lucide-react'
import { useFavoriteStore } from '../store/favoriteStore'
import { useCartStore } from '../store/cartStore'

export default function FavoritesPage() {
  const navigate = useNavigate()
  const { favorites, toggleFavorite, isFavorite } = useFavoriteStore()
  const { addItem, items } = useCartStore()

  return (
    <div className="container">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
        <button 
          onClick={() => navigate(-1)} 
          style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>
          <ArrowLeft size={24} />
        </button>
        <h2 style={{ marginLeft: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Heart size={24} fill="#ef4444" color="#ef4444" />
          Mes favoris
        </h2>
      </div>

      {favorites.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <Heart size={48} style={{ color: 'var(--color-text-muted)', margin: '0 auto 1rem', opacity: 0.5 }} />
          <h3>Aucun favori</h3>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '2rem' }}>
            Vous n'avez pas encore ajouté de photo à vos favoris.
          </p>
          <button className="btn btn-primary" onClick={() => navigate(-1)}>
            <Search size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Chercher des photos
          </button>
        </div>
      ) : (
        <>
          <p style={{ marginBottom: '1.5rem', color: 'var(--color-text-muted)' }}>
            {favorites.length} photo(s) sauvegardée(s)
          </p>
          
          <div className="gallery">
            {favorites.map((photo: any) => {
              const inCart = items.some(i => i.id === photo.id)
              const fav = isFavorite(photo.id)
              return (
                <div key={photo.id} className="photo-card" style={{ position: 'relative' }}>
                  <div onClick={() => !inCart && addItem(photo)} style={{ cursor: 'pointer' }}>
                    <img src={photo.url} alt="Sport" />
                    <div className="watermark"><span>ZOPIC</span></div>
                  </div>
                  
                  {/* Heart Button */}
                  <button 
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(photo)
                    }}
                    style={{ 
                      position: 'absolute', 
                      top: '8px', 
                      right: '8px', 
                      background: 'rgba(0,0,0,0.5)', 
                      border: 'none', 
                      borderRadius: '50%',
                      padding: '8px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: fav ? '#ef4444' : 'white',
                      transform: fav ? 'scale(1.1)' : 'scale(1)',
                      transition: 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), color 0.2s'
                    }}
                  >
                    <Heart size={20} fill={fav ? '#ef4444' : 'none'} />
                  </button>

                  {inCart && (
                    <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(3,218,198,0.3)', border: '2px solid var(--color-success)', borderRadius: '8px', pointerEvents: 'none' }}></div>
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
        </>
      )}
    </div>
  )
}
