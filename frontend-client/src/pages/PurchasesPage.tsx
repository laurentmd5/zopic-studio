import { useState } from 'react'
import { Filter, ChevronLeft, Package } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import './PurchasesPage.css'

export default function PurchasesPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'toutes' | 'telechargeables' | 'archives'>('telechargeables')

  // Mock data based on the provided mockup
  const mockPurchases = [
    {
      id: 1,
      title: "Marathon Dakar 2025",
      date: "12 Avril 2025",
      count: 9,
      expiry: "12/02/2025",
      image: "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=200&q=80",
      overlay: "102"
    },
    {
      id: 2,
      title: "Semi-Marathon de Saint-Louis",
      date: "12 janvier 2025",
      count: 9,
      expiry: "12/02/2025",
      image: "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=200&q=80",
      overlay: "102"
    },
    {
      id: 3,
      title: "Dakar 10K",
      date: "17 janvier 2025",
      count: 9,
      expiry: "06/05/2025",
      image: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=200&q=80",
      overlay: "102"
    }
  ]

  return (
    <div className="purchases-container">
      {/* Header */}
      <header className="purchases-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2 className="page-title">Mes achats</h2>
        <button className="filter-btn">
          <Filter size={20} />
        </button>
      </header>

      {/* Tabs */}
      <div className="purchases-tabs">
        <button 
          className={`purchase-tab ${activeTab === 'toutes' ? 'active' : ''}`}
          onClick={() => setActiveTab('toutes')}
        >
          Toutes
        </button>
        <button 
          className={`purchase-tab ${activeTab === 'telechargeables' ? 'active' : ''}`}
          onClick={() => setActiveTab('telechargeables')}
        >
          Téléchargeables
        </button>
        <button 
          className={`purchase-tab ${activeTab === 'archives' ? 'active' : ''}`}
          onClick={() => setActiveTab('archives')}
        >
          Archives
        </button>
      </div>

      {/* List */}
      <div className="purchases-list">
        {mockPurchases.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <Package size={48} color="var(--color-text-muted)" style={{ margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Aucun achat</h3>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Vos achats apparaîtront ici.</p>
          </div>
        ) : (
          mockPurchases.map((purchase) => (
            <div key={purchase.id} className="purchase-card">
              <div className="purchase-card-content">
                <h3 className="purchase-title">{purchase.title}</h3>
                <p className="purchase-meta">{purchase.date} • {purchase.count} achats</p>
                <p className="purchase-expiry">Disponible jusqu'au {purchase.expiry}</p>
                
                <div className="purchase-actions">
                  <button className="btn-sm btn-primary-sm">Télécharger tout (ZIP)</button>
                  <button className="btn-sm btn-outline-sm">Voir les photos</button>
                </div>
              </div>
              
              <div className="purchase-card-image">
                <img src={purchase.image} alt={purchase.title} />
                <div className="purchase-image-overlay">
                  {purchase.overlay}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
