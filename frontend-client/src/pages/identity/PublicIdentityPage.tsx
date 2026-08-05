import React from 'react';
import { Share2, MapPin, CheckCircle2, User, Activity, Link as LinkIcon } from 'lucide-react';
import './PublicIdentityPage.css';

const PublicIdentityPage: React.FC = () => {

  return (
    <div className="public-profile-container">
      {/* Navbar */}
      <nav className="public-navbar">
        <div className="public-navbar-logo">
          ZoPic
          <span>STUDIO</span>
        </div>
        <div className="public-navbar-links">
          <a href="#">Accueil</a>
          <a href="#">Compétitions</a>
          <a href="#">Photographes</a>
          <a href="#">Tarifs</a>
        </div>
        <button className="public-navbar-btn">Se connecter</button>
      </nav>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-overlay"></div>
        <div className="hero-content-wrapper">
          <div className="hero-profile-info">
            <img 
              src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80" 
              alt="Moussa Diop" 
              className="hero-avatar"
            />
            <div className="hero-details">
              <div className="hero-handle-row">
                <h1 className="hero-handle">@moussa.dkr</h1>
                <CheckCircle2 size={24} className="hero-verified" fill="currentColor" color="white" />
              </div>
              <h2 className="hero-name">Moussa Diop</h2>
              
              <div className="hero-tags">
                <div className="hero-tag">
                  <CheckCircle2 size={14} color="#D4AF37" />
                  <span>Athlétisme</span>
                </div>
                <div className="hero-tag">
                  <MapPin size={14} color="#D4AF37" />
                  <span>Coureur de fond</span>
                </div>
                <div className="hero-tag">
                  <MapPin size={14} color="#D4AF37" />
                  <span>Dakar, Sénégal</span>
                </div>
                <div className="hero-tag">
                  <User size={14} color="#D4AF37" />
                  <span>ASC Jaraaf</span>
                </div>
              </div>

              <div className="hero-stats">
                <div className="hero-stat">
                  <span className="hero-stat-value">🏅 17</span>
                  <span className="hero-stat-label">Compétitions</span>
                </div>
                <div className="hero-stat">
                  <span className="hero-stat-value">📷 246</span>
                  <span className="hero-stat-label">Photos achetées</span>
                </div>
                <div className="hero-stat">
                  <span className="hero-stat-value">📁 9</span>
                  <span className="hero-stat-label">Albums</span>
                </div>
                <div className="hero-stat">
                  <span className="hero-stat-value">📸 8</span>
                  <span className="hero-stat-label">Photographes</span>
                </div>
              </div>
            </div>
          </div>

          <div className="hero-share-block">
            <span className="share-label">Partager mon profil</span>
            <div className="qr-box">
              <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://zopic.studio/@moussa.dkr" alt="QR Code" />
            </div>
            <div className="share-actions">
              <button className="btn-copy">Copier le lien</button>
              <button className="btn-icon"><Share2 size={16} /></button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="profile-main">
        {/* Tabs */}
        <div className="profile-tabs">
          <div className="profile-tab">À propos</div>
          <div className="profile-tab active">Timeline</div>
          <div className="profile-tab">Galerie</div>
          <div className="profile-tab">Palmarès</div>
          <div className="profile-tab">Partages</div>
        </div>

        <div className="profile-columns">
          {/* Left Column (Timeline) */}
          <div className="profile-col-left">
            <h3 className="section-title">Ma carrière en images</h3>
            
            <div className="desktop-timeline">
              <div className="timeline-card">
                <div className="tc-info">
                  <div className="tc-date">12 Avril 2025</div>
                  <div className="tc-title">Marathon Dakar 2025</div>
                  <div className="tc-location">Dakar, Sénégal</div>
                </div>
                <div className="tc-stats">56 photos</div>
                <img src="https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=100&q=80" alt="Marathon" className="tc-img" />
              </div>

              <div className="timeline-card">
                <div className="tc-info">
                  <div className="tc-date">22 Février 2025</div>
                  <div className="tc-title">Semi-Marathon de Saint-Louis</div>
                  <div className="tc-location">Saint-Louis, Sénégal</div>
                </div>
                <div className="tc-stats">42 photos</div>
                <img src="https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=100&q=80" alt="Semi Marathon" className="tc-img" />
              </div>

              <div className="timeline-card">
                <div className="tc-info">
                  <div className="tc-date">5 Janvier 2025</div>
                  <div className="tc-title">Dakar 10K</div>
                  <div className="tc-location">Dakar, Sénégal</div>
                </div>
                <div className="tc-stats">38 photos</div>
                <img src="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=100&q=80" alt="Dakar 10K" className="tc-img" />
              </div>
              
              <button className="btn-view-all">Voir toutes les compétitions</button>
            </div>
          </div>

          {/* Right Column (Sidebar) */}
          <div className="profile-col-right">
            <div className="sidebar-card">
              <h4 className="sidebar-title">À propos de moi</h4>
              <p className="bio-text">
                Passionné de course à pied depuis mon plus jeune âge. Toujours en quête de nouveaux défis et de performance.
              </p>
              <div className="bio-stats">
                <div className="bio-stat"><User size={16} /> 22 ans</div>
                <div className="bio-stat"><Activity size={16} /> 1.78 m</div>
                <div className="bio-stat"><Activity size={16} /> 64 kg</div>
              </div>
            </div>

            <div className="sidebar-card">
              <h4 className="sidebar-title">Sports pratiqués</h4>
              <div className="sports-tags">
                <span className="sport-tag">Athlétisme</span>
                <span className="sport-tag">Course de fond</span>
                <span className="sport-tag">10K</span>
                <span className="sport-tag">Semi-Marathon</span>
                <span className="sport-tag">Marathon</span>
              </div>
            </div>

            <div className="sidebar-card">
              <h4 className="sidebar-title">Réseaux sociaux</h4>
              <div className="social-icons">
                <div className="social-icon"><LinkIcon size={16} /></div>
                <div className="social-icon"><LinkIcon size={16} /></div>
                <div className="social-icon"><LinkIcon size={16} /></div>
                <div className="social-icon"><LinkIcon size={16} /></div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PublicIdentityPage;
