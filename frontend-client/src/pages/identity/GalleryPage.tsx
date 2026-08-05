import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, X, Plus } from 'lucide-react';
import './GalleryPage.css';

const GalleryPage: React.FC = () => {
  const navigate = useNavigate();
  
  // Mock data for the gallery
  const [photos, setPhotos] = useState([
    "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=300&q=80",
    "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=300&q=80",
    "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=300&q=80",
    "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=300&q=80",
    "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=300&q=80"
  ]);

  const maxPhotos = 20;
  const currentCount = photos.length;
  const progressPercent = (currentCount / maxPhotos) * 100;

  const handleRemove = (indexToRemove: number) => {
    setPhotos(photos.filter((_, i) => i !== indexToRemove));
  };

  return (
    <div className="gallery-manage-container">
      {/* Header */}
      <header className="gallery-manage-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2>Ma Galerie Publique</h2>
      </header>

      <div className="gallery-manage-content">
        
        {/* Gauge Card */}
        <div className="gallery-gauge-card">
          <div className="gallery-gauge-header">
            <span className="gallery-gauge-title">Stockage Galerie</span>
            <span className="gallery-gauge-plan">Plan Basic</span>
          </div>
          <div className="gallery-progress-bar">
            <div 
              className="gallery-progress-fill" 
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
          <div className="gallery-gauge-text">
            {currentCount} / {maxPhotos} photos ajoutées
          </div>
        </div>

        {/* Grid */}
        <div className="gallery-grid">
          {photos.map((photoUrl, index) => (
            <div key={index} className="gallery-grid-item">
              <img src={photoUrl} alt={`Galerie ${index + 1}`} />
              <button 
                className="btn-remove-photo"
                onClick={() => handleRemove(index)}
              >
                <X size={14} />
              </button>
            </div>
          ))}
          
          {currentCount < maxPhotos && (
            <button 
              className="gallery-grid-add"
              onClick={() => navigate('/purchases')}
            >
              <Plus size={24} />
              <span>Ajouter</span>
            </button>
          )}
        </div>

        {/* Action Button */}
        <button 
          className="btn btn-primary"
          onClick={() => navigate('/purchases')}
        >
          Sélectionner depuis Mes Achats
        </button>

      </div>
    </div>
  );
};

export default GalleryPage;
