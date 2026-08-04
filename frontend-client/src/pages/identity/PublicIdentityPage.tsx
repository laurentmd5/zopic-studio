import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import QRCode from 'react-qr-code';
import { Share2, CheckCircle, Camera, Trophy, Image as ImageIcon, Users, X, MapPin } from 'lucide-react';
import { identityApi } from '../../api/identity';
import type { PublicAthleteProfile } from '../../api/identity';

const PublicIdentityPage: React.FC = () => {
  const { handle } = useParams<{ handle: string }>();
  const navigate = useNavigate();
  const slug = handle?.startsWith('@') ? handle.substring(1) : handle;
  const [profile, setProfile] = useState<PublicAthleteProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showQR, setShowQR] = useState(false);

  useEffect(() => {
    if (slug) {
      identityApi.getPublicProfile(slug)
        .then(data => {
          setProfile(data);
          document.title = `${data.bio ? data.bio + ' | ' : ''}ZoPic`;
          const metaDesc = document.querySelector('meta[name="description"]');
          if (metaDesc) {
             metaDesc.setAttribute("content", `Découvrez les photos sportives de ${slug} sur ZoPic.`);
          }
        })
        .catch(err => {
          console.error(err);
          setError("Profil introuvable ou privé.");
        })
        .finally(() => setLoading(false));
    }
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mb-6">
          <Camera size={32} className="text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Profil Introuvable</h2>
        <p className="text-gray-500 mb-8 max-w-sm">Ce profil n'existe pas ou a été défini comme privé par le sportif.</p>
        <button className="btn-primary w-full max-w-sm py-3 rounded-xl font-bold shadow-md" onClick={() => navigate('/')}>
          Retour à l'accueil
        </button>
      </div>
    );
  }

  const themeColors: Record<string, string> = {
    blue: 'bg-blue-600',
    red: 'bg-red-600',
    green: 'bg-[#3A4B29]',
    black: 'bg-gray-900',
  };

  const themeBg = themeColors[profile.theme_color] || themeColors['green'];
  const profileUrl = `${window.location.origin}/@${slug}`;

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Cover */}
      <div className={`h-48 w-full ${themeBg} relative rounded-b-3xl shadow-sm`}>
        {profile.cover_photo_url && (
          <img src={profile.cover_photo_url} alt="Cover" className="w-full h-full object-cover rounded-b-3xl opacity-80 mix-blend-overlay" />
        )}
        <div className="absolute top-6 right-6 flex space-x-2">
          <button 
            onClick={() => setShowQR(true)}
            className="p-2.5 bg-black/20 backdrop-blur-md rounded-full text-white hover:bg-black/40 transition shadow-sm"
          >
            <Share2 size={20} />
          </button>
        </div>
      </div>

      {/* Profile Header */}
      <div className="max-w-3xl mx-auto px-6 -mt-16 relative z-10">
        <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-28 h-28 rounded-full border-4 border-white shadow-lg overflow-hidden bg-gray-100 -mt-20 mb-4 shrink-0 relative">
              {profile.profile_photo_url ? (
                <img src={profile.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-4xl font-bold text-gray-300">
                  {slug?.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-1.5 mb-2">
                @{profile.slug}
                {profile.is_verified && <CheckCircle size={20} className="text-blue-500" />}
              </h1>
              
              <div className="text-gray-600 space-y-2 mb-4">
                {profile.bio && <p className="text-gray-800 font-medium">{profile.bio}</p>}
                <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500 font-medium mt-2">
                  {profile.club && <span className="flex items-center gap-1">🏢 {profile.club}</span>}
                  {profile.nationality && <span className="flex items-center gap-1"><MapPin size={14} /> {profile.nationality}</span>}
                </div>
              </div>

              {/* Dynamic Sport Attributes */}
              {profile.sport_attributes && Object.keys(profile.sport_attributes).length > 0 && (
                <div className="flex flex-wrap justify-center gap-2 mt-4">
                  {Object.entries(profile.sport_attributes).map(([key, value]) => (
                    <span key={key} className="px-3 py-1 bg-gray-50 border border-gray-200 text-gray-700 text-xs font-bold rounded-full capitalize">
                      {key}: {value as string}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mt-6">
          <StatCard icon={<Trophy size={20} className="text-[#3A4B29]" />} label="Événements" value={profile.statistics.competitions} />
          <StatCard icon={<Camera size={20} className="text-[#3A4B29]" />} label="Photos" value={profile.statistics.photos} />
        </div>
        <div className="grid grid-cols-2 gap-4 mt-4">
          <StatCard icon={<ImageIcon size={20} className="text-[#3A4B29]" />} label="Albums" value={profile.statistics.albums} />
          <StatCard icon={<Users size={20} className="text-[#3A4B29]" />} label="Disciplines" value={profile.statistics.disciplines} />
        </div>

        {/* Timeline Placeholder */}
        <div className="mt-8 mb-4">
          <h2 className="text-xl font-bold text-gray-900 mb-4 px-2">Carrière Sportive</h2>
          {profile.statistics.competitions > 0 ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 text-center text-gray-500 flex flex-col items-center">
               <ImageIcon size={32} className="text-gray-300 mb-3" />
               <p className="font-medium text-gray-800 mb-1">Palmarès en cours de construction</p>
               <p className="text-sm">Les événements de {slug} apparaîtront bientôt ici.</p>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center text-gray-500 flex flex-col items-center">
               <Camera size={40} className="text-gray-300 mb-4" />
               <p className="font-bold text-gray-900 mb-2">Aucune photo pour le moment</p>
               <p className="text-sm mb-6">@{profile.slug} n'a pas encore de photos publiques.</p>
            </div>
          )}
        </div>
      </div>

      {/* Share Modal */}
      {showQR && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-0">
          <div className="bg-white rounded-3xl p-6 w-full max-w-sm text-center shadow-xl mb-4 sm:mb-0 transform transition-all relative">
            <button 
              onClick={() => setShowQR(false)}
              className="absolute top-4 right-4 p-2 bg-gray-100 rounded-full text-gray-500 hover:bg-gray-200"
            >
              <X size={18} />
            </button>
            <h3 className="text-xl font-bold text-gray-900 mb-2 mt-4">Partager le profil</h3>
            <p className="text-sm text-gray-500 mb-6 px-4">Flashez ce QR Code ou copiez le lien pour partager ce profil.</p>
            
            <div className="bg-gray-50 p-6 rounded-2xl inline-block shadow-inner border border-gray-100 mb-8">
              <QRCode value={profileUrl} size={180} fgColor="#3A4B29" />
            </div>
            
            <div className="flex flex-col gap-3">
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(profileUrl);
                  alert("Lien copié !");
                  setShowQR(false);
                }}
                className="w-full py-3.5 bg-gray-900 text-white font-bold rounded-xl shadow-md hover:bg-gray-800 transition active:scale-[0.98]"
              >
                Copier le lien
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: number }) => (
  <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center">
    <div className="bg-gray-50 p-2.5 rounded-full mb-3">{icon}</div>
    <div className="text-3xl font-black text-gray-900 mb-1">{value}</div>
    <div className="text-xs font-bold text-gray-400 uppercase tracking-widest">{label}</div>
  </div>
);

export default PublicIdentityPage;
