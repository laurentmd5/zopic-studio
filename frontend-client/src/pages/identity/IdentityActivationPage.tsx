import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { identityApi } from '../../api/identity';
import { Check, ArrowRight, Loader2, Link as LinkIcon, User } from 'lucide-react';

const IdentityActivationPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [baseSlug, setBaseSlug] = useState('');
  const [selectedSlug, setSelectedSlug] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Choose slug
  const handleCheckSlug = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!baseSlug) return;
    
    setLoading(true);
    setError(null);
    try {
      const sugs = await identityApi.getSlugSuggestions(baseSlug.toLowerCase().replace(/[^a-z0-9._-]/g, ''));
      setSuggestions(sugs);
      if (sugs.includes(baseSlug)) {
         setSelectedSlug(baseSlug);
      }
      setStep(2);
    } catch (err) {
      setError("Erreur lors de la vérification du slug.");
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async () => {
    if (!selectedSlug) return;
    setLoading(true);
    try {
      // Step 3: API Create and magic transition
      setStep(3); // Shows magic import screen
      await identityApi.createProfile({
        slug: selectedSlug,
        is_public: "PUBLIC",
        theme_color: "blue"
      });
      
      // Simulate magic loading time for UX
      setTimeout(() => {
        navigate(`/@${selectedSlug}`);
      }, 2000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de la création.");
      setStep(2); // Go back on error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center text-blue-600 mb-4">
          <User size={48} className="p-3 bg-blue-100 rounded-full" />
        </div>
        <h2 className="text-center text-3xl font-extrabold text-gray-900">
          Mon Identité Sportive
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          La vitrine numérique officielle de votre carrière
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-xl sm:px-10">
          
          {step === 1 && (
            <form onSubmit={handleCheckSlug} className="space-y-6">
              <div>
                <label htmlFor="slug" className="block text-sm font-medium text-gray-700">
                  Choisissez votre lien public
                </label>
                <div className="mt-1 flex rounded-md shadow-sm">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm font-medium">
                    zopic.studio/@
                  </span>
                  <input
                    type="text"
                    name="slug"
                    id="slug"
                    value={baseSlug}
                    onChange={(e) => setBaseSlug(e.target.value)}
                    className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="moussa.dkr"
                    required
                  />
                </div>
              </div>
              
              {error && <p className="text-red-500 text-sm">{error}</p>}
              
              <button
                type="submit"
                disabled={loading || !baseSlug}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition"
              >
                {loading ? <Loader2 className="animate-spin" size={20} /> : "Vérifier la disponibilité"}
              </button>
            </form>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Sélectionnez votre URL</h3>
              
              <div className="space-y-3">
                {suggestions.map((sug) => (
                  <button
                    key={sug}
                    onClick={() => setSelectedSlug(sug)}
                    className={`w-full flex items-center justify-between px-4 py-3 border rounded-xl transition ${
                      selectedSlug === sug ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <span className="font-medium text-gray-900">@{sug}</span>
                    {selectedSlug === sug && <Check className="text-blue-500" size={20} />}
                  </button>
                ))}
              </div>

              {error && <p className="text-red-500 text-sm">{error}</p>}
              
              <button
                onClick={handleActivate}
                disabled={!selectedSlug || loading}
                className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gray-900 hover:bg-black focus:outline-none transition disabled:opacity-50"
              >
                <span>Créer mon identité</span>
                <ArrowRight size={16} />
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="flex flex-col items-center justify-center py-8 space-y-6">
              <div className="relative">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center animate-pulse">
                  <LinkIcon className="text-blue-600" size={32} />
                </div>
                <div className="absolute top-0 right-0 -mt-1 -mr-1">
                  <span className="flex h-4 w-4">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-4 w-4 bg-blue-500"></span>
                  </span>
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Import automatique...</h3>
              <p className="text-center text-sm text-gray-500">
                ZoPic analyse votre historique d'achats pour construire vos statistiques magiques.
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default IdentityActivationPage;
