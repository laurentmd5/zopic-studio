import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Camera, Search, MapPin, ChevronRight, Bell } from 'lucide-react';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  if (isLoggedIn) {
    return (
      <div className="home-container logged-in">
        <header className="home-header-logged">
          <div className="home-user-info">
            <img 
              src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80" 
              alt="Moussa" 
              className="home-user-avatar" 
            />
            <div className="home-user-text">
              <span className="home-greeting">Bonjour,</span>
              <h2 className="home-name">Moussa Diop</h2>
            </div>
          </div>
          <button className="btn-icon">
            <Bell size={24} />
          </button>
        </header>

        <div className="home-content-scroll">
          {/* Magic Alert for new photos */}
          <div className="magic-alert-card" onClick={() => navigate('/competition/1/search')}>
            <div className="magic-alert-icon">
              <Camera size={20} />
            </div>
            <div className="magic-alert-text">
              <h4>3 nouvelles photos trouvées !</h4>
              <p>Notre IA vous a repéré au Marathon de Dakar.</p>
            </div>
            <ChevronRight size={20} className="magic-alert-arrow" />
          </div>

          {/* Quick Search */}
          <div className="quick-search-section">
            <div className="search-bar" onClick={() => navigate('/search')}>
              <Search size={20} className="search-icon" />
              <span>Rechercher par dossard ou selfie</span>
            </div>
          </div>

          {/* Targeted Ad Space (Decathlon) */}
          <div className="targeted-ad-card">
            <div className="ad-badge">Sponsorisé</div>
            <img src="https://images.unsplash.com/photo-1571008882538-4f4711929944?w=400&q=80" alt="Equipement course" className="ad-image" />
            <div className="ad-content">
              <h4>Decathlon Dakar</h4>
              <p>Découvrez notre nouvelle gamme running spéciale fond. -20% pour les membres ZoPic !</p>
              <button className="btn-ad-action">Profiter de l'offre</button>
            </div>
          </div>

          {/* Recommended Competitions */}
          <div className="section-title-wrapper">
            <h3>Compétitions recommandées</h3>
            <span className="see-all">Voir tout</span>
          </div>

          <div className="competition-cards-horizontal">
            <div className="competition-card-mini" onClick={() => navigate('/competition/2')}>
              <img src="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=300&q=80" alt="Course" />
              <div className="comp-mini-info">
                <h4>Semi-Marathon Eiffage</h4>
                <span><MapPin size={12} /> Dakar, SN</span>
              </div>
            </div>
            <div className="competition-card-mini">
              <img src="https://images.unsplash.com/photo-1530549387789-4c1017266635?w=300&q=80" alt="Course" />
              <div className="comp-mini-info">
                <h4>10km de Thiès</h4>
                <span><MapPin size={12} /> Thiès, SN</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // LOGGED OUT VIEW (Visitor)
  return (
    <div className="home-container">
      <div className="home-content">
        <div className="logo-container">
          <h1 className="logo">
            <span className="logo-z">Z</span>
            <span className="logo-o">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <circle cx="12" cy="12" r="4" fill="currentColor"/>
              </svg>
            </span>
            <span className="logo-pic">Pic</span>
          </h1>
          <span className="logo-subtitle">STUDIO</span>
        </div>

        <h2 className="main-title">
          Vos meilleurs<br />
          moments sportifs<br />
          en images
        </h2>

        <p className="main-subtitle">
          Retrouvez, achetez et téléchargez<br />
          vos photos de compétition
        </p>
      </div>

      <div className="home-background">
        <img src="/hero_athlete.jpg" alt="Athlete" className="athlete-img" />
        <div className="gradient-overlay"></div>
      </div>

      <div className="home-actions">
        <button 
          className="btn btn-primary"
          onClick={() => navigate('/competition/1/search')}
        >
          Trouver mes photos
        </button>
        
        <button 
          className="btn btn-white"
          onClick={() => navigate('/auth')}
        >
          Se connecter / S'inscrire
        </button>
      </div>
    </div>
  );
};

export default HomePage;
