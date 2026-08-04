import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { identityApi } from '../../api/identity';
import type { PublicAthleteProfile } from '../../api/identity';
import { Save, Loader2, ArrowLeft, Camera, Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';

const EditIdentityPage: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<PublicAthleteProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sportKey, setSportKey] = useState('');
  const [sportValue, setSportValue] = useState('');

  useEffect(() => {
    identityApi.getMyProfile()
      .then(data => setProfile(data))
      .catch(err => {
         console.error(err);
         toast.error("Impossible de charger le profil");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    if (!profile) return;
    setProfile({
      ...profile,
      [e.target.name]: e.target.value
    });
  };

  const handleAddAttribute = () => {
    if (!profile || !sportKey || !sportValue) return;
    setProfile({
      ...profile,
      sport_attributes: {
        ...(profile.sport_attributes || {}),
        [sportKey.toLowerCase()]: sportValue
      }
    });
    setSportKey('');
    setSportValue('');
  };

  const handleRemoveAttribute = (key: string) => {
    if (!profile || !profile.sport_attributes) return;
    const newAttrs = { ...profile.sport_attributes };
    delete newAttrs[key];
    setProfile({
      ...profile,
      sport_attributes: newAttrs
    });
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await identityApi.updateProfile({
        bio: profile.bio,
        club: profile.club,
        nationality: profile.nationality,
        theme_color: profile.theme_color,
        sport_attributes: profile.sport_attributes,
        is_public: profile.is_public
      });
      toast.success("Profil mis à jour !");
      setTimeout(() => navigate(`/@${profile.slug}`), 1000);
    } catch (err) {
      toast.error("Erreur lors de la sauvegarde.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!profile) return <div className="min-h-screen flex items-center justify-center bg-gray-50">Erreur</div>;

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="bg-white px-6 pt-8 pb-4 border-b border-gray-100 shadow-sm sticky top-0 z-40 flex items-center justify-between">
        <div className="flex items-center">
          <button onClick={() => navigate(-1)} className="text-gray-900">
            <ArrowLeft size={24} />
          </button>
          <h2 className="ml-4 text-xl font-bold text-gray-900">Mon Profil</h2>
        </div>
        <button 
          onClick={handleSave}
          disabled={saving}
          className="text-[#3A4B29] font-bold text-sm"
        >
          {saving ? 'Enregistrement...' : 'Enregistrer'}
        </button>
      </div>

      <div className="p-4 space-y-6 max-w-2xl mx-auto">
        
        {/* Profile Photo Mock */}
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm flex flex-col items-center">
          <div className="w-24 h-24 rounded-full bg-gray-100 border-4 border-white shadow-md flex items-center justify-center relative mb-4">
            <Camera size={32} className="text-gray-400" />
            <div className="absolute bottom-0 right-0 bg-[#3A4B29] rounded-full p-2 border-2 border-white cursor-pointer">
              <Plus size={14} className="text-white font-bold" />
            </div>
          </div>
          <h3 className="font-bold text-gray-900">@{profile.slug}</h3>
          <p className="text-xs text-gray-500 mt-1">Lien public : zopic.studio/@{profile.slug}</p>
        </div>

        {/* General Info */}
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-4">
          <h3 className="font-bold text-gray-900 border-b border-gray-100 pb-2">Informations Générales</h3>
          
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Bio</label>
            <textarea 
              name="bio"
              value={profile.bio || ''}
              onChange={handleChange}
              placeholder="Parlez de votre parcours sportif..."
              className="w-full rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29] transition-all"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Club / Équipe</label>
            <input 
              type="text"
              name="club"
              value={profile.club || ''}
              onChange={handleChange}
              placeholder="Ex: AS Dakar Sacré-Cœur"
              className="w-full rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29] transition-all"
            />
          </div>
          
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Ville / Pays</label>
            <input 
              type="text"
              name="nationality"
              value={profile.nationality || ''}
              onChange={handleChange}
              placeholder="Ex: Dakar, Sénégal"
              className="w-full rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29] transition-all"
            />
          </div>
        </div>

        {/* Sport Attributes */}
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-4">
          <h3 className="font-bold text-gray-900 border-b border-gray-100 pb-2">Caractéristiques Sportives</h3>
          
          <div className="flex gap-2">
            <input 
              type="text"
              placeholder="Type (ex: Poste)"
              value={sportKey}
              onChange={e => setSportKey(e.target.value)}
              className="flex-1 rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29]"
            />
            <input 
              type="text"
              placeholder="Valeur (ex: Ailier)"
              value={sportValue}
              onChange={e => setSportValue(e.target.value)}
              className="flex-1 rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29]"
            />
            <button 
              onClick={handleAddAttribute}
              className="bg-[#3A4B29] text-white px-4 rounded-xl flex items-center justify-center shadow-sm"
            >
              <Plus size={20} />
            </button>
          </div>
          
          {profile.sport_attributes && Object.keys(profile.sport_attributes).length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {Object.entries(profile.sport_attributes).map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 bg-[#E8F5E9] text-[#3A4B29] px-3 py-1.5 rounded-full text-sm font-medium">
                  <span className="capitalize">{k}: {v as string}</span>
                  <button onClick={() => handleRemoveAttribute(k)} className="hover:text-red-500 opacity-70 hover:opacity-100">
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settings */}
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-4 mb-8">
          <h3 className="font-bold text-gray-900 border-b border-gray-100 pb-2">Paramètres du profil</h3>
          
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Visibilité du profil public</label>
            <select
              name="is_public"
              value={profile.is_public}
              onChange={handleChange}
              className="w-full rounded-xl border-gray-200 bg-gray-50 p-3 text-sm focus:border-[#3A4B29] focus:ring-1 focus:ring-[#3A4B29]"
            >
              <option value="PUBLIC">Public (Recommandé, indexé sur Google)</option>
              <option value="LINK_ONLY">Lien Uniquement (Caché des moteurs)</option>
              <option value="PRIVATE">Privé (Visible par vous seul)</option>
            </select>
          </div>
        </div>

        <button 
          onClick={handleSave}
          disabled={saving}
          className="w-full py-4 bg-[#3A4B29] text-white font-bold rounded-xl shadow-lg text-lg flex items-center justify-center gap-2"
        >
          {saving ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div> : <Save size={20} />}
          {saving ? 'Enregistrement...' : 'Enregistrer les modifications'}
        </button>

      </div>
    </div>
  );
};

export default EditIdentityPage;
