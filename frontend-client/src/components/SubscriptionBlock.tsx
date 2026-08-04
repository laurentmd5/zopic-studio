import { useState } from 'react';
import { Check, Star, Shield } from 'lucide-react';

interface Plan {
  id: string;
  name: string;
  price: number;
  features: string[];
  recommended?: boolean;
}

const plans: Plan[] = [
  {
    id: 'basic',
    name: 'Profil Standard',
    price: 2000,
    features: [
      'Profil public indexé (SEO)',
      'Statistiques de base',
      'Galerie de photos',
      'QR Code de partage'
    ]
  },
  {
    id: 'pro',
    name: 'Profil Pro',
    price: 5000,
    features: [
      'Toutes les fonctionnalités Standard',
      'Génération de CV Sportif (PDF)',
      'Statistiques avancées',
      'Badge vérifié',
      'Recherche de sponsors'
    ],
    recommended: true
  }
];

export default function SubscriptionBlock() {
  const [selectedPlan, setSelectedPlan] = useState<string>('basic');

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-8">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Passez au niveau supérieur</h3>
        <p className="text-sm text-gray-500">
          Choisissez l'abonnement qui correspond à vos ambitions.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {plans.map((plan) => (
          <div
            key={plan.id}
            onClick={() => setSelectedPlan(plan.id)}
            className={`relative rounded-xl p-5 border-2 cursor-pointer transition-all duration-200 ${
              selectedPlan === plan.id
                ? 'border-[#3A4B29] bg-[#F7F9F6]'
                : 'border-gray-100 bg-white hover:border-gray-200'
            }`}
          >
            {plan.recommended && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-[#3A4B29] text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider flex items-center gap-1">
                <Star size={10} fill="white" /> Recommandé
              </div>
            )}
            
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-bold text-gray-900">{plan.name}</h4>
              <div className="flex flex-col items-end">
                <span className="font-black text-xl text-gray-900">{plan.price}</span>
                <span className="text-[10px] font-bold text-gray-400 uppercase">FCFA / Mois</span>
              </div>
            </div>

            <ul className="space-y-2 mb-6">
              {plan.features.map((feature, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                  <Check size={16} className="text-[#3A4B29] mt-0.5 shrink-0" />
                  <span className="leading-tight">{feature}</span>
                </li>
              ))}
            </ul>

            <button
              className={`w-full py-2.5 rounded-lg font-bold text-sm transition-colors ${
                selectedPlan === plan.id
                  ? 'bg-[#3A4B29] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {selectedPlan === plan.id ? 'Abonnement Actuel' : 'Choisir ce forfait'}
            </button>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-6 border-t border-gray-100 flex items-center justify-center gap-2 text-xs text-gray-400">
        <Shield size={14} /> Paiement sécurisé et sans engagement
      </div>
    </div>
  );
}
