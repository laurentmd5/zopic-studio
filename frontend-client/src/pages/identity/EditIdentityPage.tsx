import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Camera, Eye } from 'lucide-react';
import './EditIdentityPage.css';

const EditIdentityPage: React.FC = () => {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    nomComplet: 'Moussa Diop',
    discipline: 'Athlétisme',
    role: 'Coureur de fond',
    club: 'ASC Jaraaf',
    ville: 'Dakar, Sénégal',
    bio: 'Passionné de course à pied depuis mon plus jeune âge. Toujours en quête de nouveaux défis et de performance.',
    age: '22',
    taille: '1.78',
    poids: '64',
    instagram: '',
    tiktok: ''
  });

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      navigate(-1);
    }, 1000);
  };

  return (
    <div className="edit-profile-container">
      {/* Header */}
      <header className="edit-profile-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2 className="page-title">Modifier mon identité</h2>
      </header>

      <div className="edit-profile-content">
        {/* Avatar Section */}
        <div className="avatar-section">
          <div className="avatar-wrapper">
            <img 
              src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80" 
              alt="Profil" 
              className="avatar-img" 
            />
            <button className="avatar-edit-btn">
              <Camera size={16} />
            </button>
          </div>
        </div>

        {/* Form Fields */}
        <div className="form-group">
          <label className="form-label">Nom complet</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              value={formData.nomComplet}
              onChange={(e) => setFormData({...formData, nomComplet: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Discipline</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="ex: Athlétisme, Natation..."
              value={formData.discipline}
              onChange={(e) => setFormData({...formData, discipline: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Rôle / Spécialité</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="ex: Coureur de fond, Sprinteur..."
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Club</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="ex: ASC Jaraaf"
              value={formData.club}
              onChange={(e) => setFormData({...formData, club: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Ville et Pays</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="ex: Dakar, Sénégal"
              value={formData.ville}
              onChange={(e) => setFormData({...formData, ville: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">À propos de moi (Bio)</label>
          <div className="form-input-wrapper">
            <textarea 
              className="form-input" 
              style={{ minHeight: '80px', paddingTop: '0.85rem' }}
              placeholder="Racontez votre parcours..."
              value={formData.bio}
              onChange={(e) => setFormData({...formData, bio: e.target.value})}
            ></textarea>
          </div>
        </div>

        <div className="form-row-3">
          <div className="form-group">
            <label className="form-label">Âge</label>
            <div className="form-input-wrapper">
              <input 
                type="text" 
                className="form-input" 
                placeholder="22 ans"
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Taille</label>
            <div className="form-input-wrapper">
              <input 
                type="text" 
                className="form-input" 
                placeholder="1.78 m"
                value={formData.taille}
                onChange={(e) => setFormData({...formData, taille: e.target.value})}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Poids</label>
            <div className="form-input-wrapper">
              <input 
                type="text" 
                className="form-input" 
                placeholder="64 kg"
                value={formData.poids}
                onChange={(e) => setFormData({...formData, poids: e.target.value})}
              />
            </div>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Instagram (@)</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="@votre.compte"
              value={formData.instagram}
              onChange={(e) => setFormData({...formData, instagram: e.target.value})}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">TikTok (@)</label>
          <div className="form-input-wrapper">
            <input 
              type="text" 
              className="form-input" 
              placeholder="@votre.compte"
              value={formData.tiktok}
              onChange={(e) => setFormData({...formData, tiktok: e.target.value})}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="edit-profile-actions">
          <button className="btn-save" onClick={handleSave}>
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
          
          <button className="btn-preview" onClick={() => navigate('/@moussa.dkr')}>
            <Eye size={18} />
            <span>Aperçu de mon profil</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditIdentityPage;
