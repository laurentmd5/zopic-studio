import React, { useState } from 'react'
import { Check, Star, Zap, Crown } from 'lucide-react'
import toast from 'react-hot-toast'
import styles from './Billing.module.css'

const plans = [
  {
    id: 'starter',
    name: 'Starter',
    icon: <Star size={24} className={styles.planIcon} />,
    storage: '200 Go',
    price: '6 500 FCFA',
    period: '/ mois',
    features: ['Upload massif', 'Watermark automatique', 'Détection faciale', 'Jusqu\'à 200 Go de stockage'],
    recommended: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    icon: <Zap size={24} className={styles.planIcon} />,
    storage: '1 To',
    price: '16 500 FCFA',
    period: '/ mois',
    features: ['Upload massif', 'Watermark automatique', 'Détection faciale', 'Jusqu\'à 1 To de stockage', 'Support prioritaire'],
    recommended: true,
  },
  {
    id: 'studio',
    name: 'Studio',
    icon: <Crown size={24} className={styles.planIcon} />,
    storage: '3 To',
    price: '39 000 FCFA',
    period: '/ mois',
    features: ['Upload massif', 'Watermark automatique', 'Détection faciale', 'Jusqu\'à 3 To de stockage', 'API Access', 'Support dédié'],
    recommended: false,
  }
]

const Billing: React.FC = () => {
  const [currentPlan, setCurrentPlan] = useState('starter')

  const handleSubscribe = (planId: string, planName: string) => {
    // MVP Simulation
    toast.loading('Redirection vers la page de paiement (Simulation)...', { duration: 2000 })
    setTimeout(() => {
      setCurrentPlan(planId)
      toast.success(`Félicitations ! Vous êtes passé au plan ${planName}.`)
    }, 2500)
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Abonnements & Stockage</h2>
        <p className={styles.subtitle}>Gérez votre espace de stockage cloud et développez votre activité.</p>
      </div>

      <div className={styles.currentStatus}>
        <h3>Plan actuel : <span className={styles.highlight}>{plans.find(p => p.id === currentPlan)?.name}</span></h3>
        <p>Prochain prélèvement le 15 Septembre 2026</p>
      </div>

      <div className={styles.plansGrid}>
        {plans.map((plan) => (
          <div key={plan.id} className={`${styles.planCard} ${plan.recommended ? styles.recommended : ''}`}>
            {plan.recommended && <div className={styles.badge}>Recommandé</div>}
            
            <div className={styles.planHeader}>
              <div className={styles.iconWrapper}>
                {plan.icon}
              </div>
              <h3 className={styles.planName}>{plan.name}</h3>
              <div className={styles.planStorage}>{plan.storage}</div>
            </div>

            <div className={styles.planPrice}>
              <span className={styles.amount}>{plan.price}</span>
              <span className={styles.period}>{plan.period}</span>
            </div>

            <ul className={styles.featuresList}>
              {plan.features.map((feat, idx) => (
                <li key={idx}>
                  <Check size={18} className={styles.checkIcon} />
                  <span>{feat}</span>
                </li>
              ))}
            </ul>

            <button 
              className={`${styles.actionBtn} ${currentPlan === plan.id ? styles.currentBtn : ''}`}
              onClick={() => handleSubscribe(plan.id, plan.name)}
              disabled={currentPlan === plan.id}
            >
              {currentPlan === plan.id ? 'Plan Actuel' : 'Choisir ce plan'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Billing
