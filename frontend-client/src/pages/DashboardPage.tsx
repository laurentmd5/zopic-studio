import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Share2, User, Image as ImageIcon, 
  Clock, Trophy, Link as LinkIcon, 
  CreditCard, BarChart2, ChevronRight,
  MapPin, CheckCircle2
} from 'lucide-react';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      {/* Hero Banner Header (Identique à l'aperçu public) */}
      <div className="dashboard-hero">
        <div className="dashboard-hero-overlay"></div>
        <div className="dashboard-hero-content">
          
          <div className="dh-top">
            <img 
              src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80" 
              alt="Avatar" 
              className="dh-avatar"
            />
            <div className="dh-info">
              <div className="dh-handle-row">
                <h1 className="dh-handle">@moussa.dkr</h1>
                <CheckCircle2 size={18} className="dh-verified" fill="currentColor" color="white" />
              </div>
              <h2 className="dh-name">Moussa Diop</h2>
              
              <div className="dh-tags">
                <div className="dh-tag">
                  <CheckCircle2 size={12} color="#D4AF37" />
                  <span>Athlétisme</span>
                </div>
                <div className="dh-tag">
                  <MapPin size={12} color="#D4AF37" />
                  <span>Coureur de fond</span>
                </div>
                <div className="dh-tag">
                  <MapPin size={12} color="#D4AF37" />
                  <span>Dakar, Sénégal</span>
                </div>
                <div className="dh-tag">
                  <User size={12} color="#D4AF37" />
                  <span>ASC Jaraaf</span>
                </div>
              </div>
            </div>
          </div>

          <div className="dh-stats">
            <div className="dh-stat">
              <span className="dh-stat-val">🏅 17</span>
              <span className="dh-stat-label">Compétitions</span>
            </div>
            <div className="dh-stat">
              <span className="dh-stat-val">📷 246</span>
              <span className="dh-stat-label">Photos achetées</span>
            </div>
            <div className="dh-stat">
              <span className="dh-stat-val">📁 9</span>
              <span className="dh-stat-label">Albums</span>
            </div>
            <div className="dh-stat">
              <span className="dh-stat-val">📸 8</span>
              <span className="dh-stat-label">Photographes</span>
            </div>
          </div>

          <div className="dh-share-section">
            <div className="dh-share-left">
              <span className="dh-share-label">Partager mon profil</span>
              <div className="dh-share-actions">
                <button className="btn-copy">Copier le lien</button>
                <button className="btn-share-icon"><Share2 size={16} /></button>
              </div>
            </div>
            <div className="dh-qr">
              <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://zopic.studio/@moussa.dkr" alt="QR Code" />
            </div>
          </div>

        </div>
      </div>

      <div className="dashboard-content">
        {/* Contenu Profil */}
        <div className="menu-section">
          <h2 className="menu-section-title">Gérer mon contenu</h2>
          <div className="menu-list">
            
            <div className="menu-item" onClick={() => navigate('/profile/edit')}>
              <div className="menu-icon-wrapper icon-info">
                <User size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Mes informations</div>
                <div className="menu-item-subtitle">Bio, mensurations, réseaux sociaux</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

            <div className="menu-item" onClick={() => navigate('/profile/gallery')}>
              <div className="menu-icon-wrapper icon-gallery">
                <ImageIcon size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Ma Galerie</div>
                <div className="menu-item-subtitle">Sélectionnez vos meilleures photos</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

            <div className="menu-item" onClick={() => navigate('/timeline')}>
              <div className="menu-icon-wrapper icon-timeline">
                <Clock size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Ma Timeline</div>
                <div className="menu-item-subtitle">Vos compétitions passées</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

            <div className="menu-item">
              <div className="menu-icon-wrapper icon-trophy">
                <Trophy size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Mon Palmarès</div>
                <div className="menu-item-subtitle">Médailles, victoires et records</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

            <div className="menu-item" onClick={() => navigate('/profile/shares')}>
              <div className="menu-icon-wrapper icon-share">
                <LinkIcon size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Mes Partages</div>
                <div className="menu-item-subtitle">Articles de presse et liens utiles</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

          </div>
        </div>

        {/* Compte */}
        <div className="menu-section">
          <h2 className="menu-section-title">Mon Compte</h2>
          <div className="menu-list">
            
            <div className="menu-item" onClick={() => navigate('/identity/activate')}>
              <div className="menu-icon-wrapper icon-sub">
                <CreditCard size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Mon Abonnement</div>
                <div className="menu-item-subtitle">Plan PRO - Gérer mon offre</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

            <div className="menu-item">
              <div className="menu-icon-wrapper" style={{ color: '#6b7280', backgroundColor: '#f3f4f6' }}>
                <BarChart2 size={20} />
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">Mes Statistiques</div>
                <div className="menu-item-subtitle">Vues et interactions sur votre profil</div>
              </div>
              <ChevronRight size={18} className="menu-item-chevron" />
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;
