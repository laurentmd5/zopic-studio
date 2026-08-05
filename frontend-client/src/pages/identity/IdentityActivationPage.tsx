import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ChevronLeft } from 'lucide-react';
import './IdentityActivationPage.css';

const IdentityActivationPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="subscription-container">
      {/* Header with Back Button */}
      <header className="subscription-top-nav">
        <button onClick={() => navigate(-1)} className="back-btn-light">
          <ChevronLeft size={28} />
        </button>
      </header>

      {/* Hero Section */}
      <div className="subscription-hero">
        <div className="subscription-hero-overlay"></div>
        <div className="subscription-hero-content">
          <h3>Passez au niveau supérieur</h3>
          <h1>Mon Identité Sportive</h1>
          <p>Débloquez votre vitrine professionnelle et toutes les fonctionnalités avancées.</p>
        </div>
      </div>

      <div className="pricing-cards">
        {/* BASIC PLAN */}
        <div className="pricing-card">
          <div className="card-header">
            <h4 className="card-title">BASIC</h4>
            <div className="card-price">
              <span className="price-amount">2 000</span>
              <span className="price-currency">FCFA <span className="price-period">/mois</span></span>
            </div>
          </div>
          
          <div className="features-list">
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Profil public</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Statistiques de base</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Galerie (20 photos)</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>QR Code</span>
            </div>
          </div>
          
          <button className="btn-plan btn-basic" onClick={() => navigate('/profile/edit')}>
            Choisir Basic
          </button>
        </div>

        {/* PRO PLAN */}
        <div className="pricing-card pro">
          <div className="card-header">
            <span className="badge-recommended">Recommandé</span>
            <h4 className="card-title">PRO</h4>
            <div className="card-price">
              <span className="price-amount">5 000</span>
              <span className="price-currency">FCFA <span className="price-period">/mois</span></span>
            </div>
          </div>
          
          <div className="features-list">
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Tout Basic +</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>CV sportif (PDF)</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Statistiques avancées</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Galerie illimitée</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={14} className="feature-icon" />
              <span>Badge vérifié</span>
            </div>
          </div>
          
          <button className="btn-plan btn-pro" onClick={() => navigate('/profile/edit')}>
            Choisir Pro
          </button>
        </div>
      </div>

      <div className="subscription-footer">
        <p>Résiliable à tout moment. Paiement sécurisé.</p>
        <a href="#avantages">Voir tous les avantages</a>
      </div>
    </div>
  );
};

export default IdentityActivationPage;
