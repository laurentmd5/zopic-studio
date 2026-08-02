import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera, ShieldCheck, Trophy, ArrowRight, CheckCircle2 } from 'lucide-react'
import { useAuthStore } from '../store/useAuthStore'
import styles from './Login.module.css'
import toast from 'react-hot-toast'

type Step = 'phone' | 'otp' | 'profile' | 'carousel' | 'subscription'

const Login: React.FC = () => {
  const [step, setStep] = useState<Step>('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  
  // Profile state
  const [fullName, setFullName] = useState('')
  const [accountType, setAccountType] = useState('independent')
  const [city, setCity] = useState('')
  const [selectedSports, setSelectedSports] = useState<string[]>([])

  const [carouselIndex, setCarouselIndex] = useState(0)

  const setToken = useAuthStore(state => state.setToken)
  const setUser = useAuthStore(state => state.setUser)
  const navigate = useNavigate()

  const sportsList = ['Football', 'Lutte', 'Basketball', 'Athlétisme', 'Cyclisme', 'Volleyball', 'Tennis', 'Arts martiaux', 'Natation']

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (phone.length < 9) {
      toast.error('Numéro invalide')
      return
    }
    toast.success('Code OTP envoyé !')
    setStep('otp')
  }

  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (otp !== '123456') {
      toast.error('Code invalide. Essayez 123456')
      return
    }
    setStep('profile')
  }

  const toggleSport = (sport: string) => {
    if (selectedSports.includes(sport)) {
      setSelectedSports(prev => prev.filter(s => s !== sport))
    } else {
      setSelectedSports(prev => [...prev, sport])
    }
  }

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!fullName || !city || selectedSports.length === 0) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }
    setStep('carousel')
  }

  const handleFinish = () => {
    // Authenticate and redirect
    setToken('token-pro-123')
    setUser({ name: fullName, role: 'photographer' })
    navigate('/')
    toast.success('Bienvenue sur ZoPic Studio !')
  }

  return (
    <div className={styles.loginContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.branding}>
          <Camera size={48} className={styles.logoIcon} />
          <h1>ZoPic Photographe</h1>
          <p>Le studio ultime pour les professionnels du sport.</p>
        </div>
      </div>

      <div className={styles.rightPanel}>
        <div className={styles.formWrapper}>
          
          {step === 'phone' && (
            <form onSubmit={handlePhoneSubmit} className={styles.form}>
              <div className={styles.headerText}>
                <h2>Connexion / Inscription</h2>
                <p>Entrez votre numéro pour continuer (Friction Zéro)</p>
              </div>
              <div className={styles.inputGroup}>
                <label>Numéro de téléphone</label>
                <input
                  type="tel"
                  placeholder="+221 77 123 45 67"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  autoFocus
                />
              </div>
              <button type="submit" className={styles.submitBtn}>
                Continuer <ArrowRight size={18} />
              </button>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleOtpSubmit} className={styles.form}>
              <div className={styles.headerText}>
                <h2>Vérification</h2>
                <p>Un code a été envoyé au {phone}</p>
              </div>
              <div className={styles.inputGroup}>
                <label>Code OTP (Tapez 123456)</label>
                <input
                  type="text"
                  maxLength={6}
                  placeholder="------"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className={styles.otpInput}
                  autoFocus
                />
              </div>
              <button type="submit" className={styles.submitBtn}>
                Vérifier
              </button>
            </form>
          )}

          {step === 'profile' && (
            <form onSubmit={handleProfileSubmit} className={styles.formProfile}>
              <div className={styles.headerText}>
                <h2>Complétez votre profil</h2>
                <p>Rejoignez la communauté des créateurs sportifs</p>
              </div>
              
              <div className={styles.inputGroup}>
                <label>Nom Complet ou Nom du Studio *</label>
                <input required type="text" value={fullName} onChange={e => setFullName(e.target.value)} />
              </div>

              <div className={styles.inputGroup}>
                <label>Type de compte *</label>
                <select value={accountType} onChange={e => setAccountType(e.target.value)}>
                  <option value="independent">Photographe indépendant</option>
                  <option value="studio">Studio photo</option>
                  <option value="organization">Organisation sportive</option>
                </select>
              </div>

              <div className={styles.inputGroup}>
                <label>Ville *</label>
                <input required type="text" placeholder="Ex: Dakar" value={city} onChange={e => setCity(e.target.value)} />
              </div>

              <div className={styles.inputGroup}>
                <label>Sports couverts *</label>
                <div className={styles.sportsGrid}>
                  {sportsList.map(sport => (
                    <div 
                      key={sport} 
                      className={`${styles.sportChip} ${selectedSports.includes(sport) ? styles.selected : ''}`}
                      onClick={() => toggleSport(sport)}
                    >
                      {sport}
                    </div>
                  ))}
                </div>
              </div>

              <button type="submit" className={styles.submitBtn}>
                Créer mon profil
              </button>
            </form>
          )}

          {step === 'carousel' && (
            <div className={styles.carouselWrapper}>
              {carouselIndex === 0 && (
                <div className={styles.carouselSlide}>
                  <ShieldCheck size={64} className={styles.slideIcon} />
                  <h2>Protégez vos photos</h2>
                  <p>ZoPic applique automatiquement un filigrane sur vos épreuves pour empêcher le vol avant achat.</p>
                </div>
              )}
              {carouselIndex === 1 && (
                <div className={styles.carouselSlide}>
                  <Trophy size={64} className={styles.slideIcon} />
                  <h2>Gérez vos compétitions</h2>
                  <p>Navétanes, Marathons, Combats... Organisez vos épreuves et laissez notre IA taguer les athlètes.</p>
                </div>
              )}
              
              <div className={styles.carouselControls}>
                {carouselIndex < 1 ? (
                  <button onClick={() => setCarouselIndex(carouselIndex + 1)} className={styles.submitBtn}>
                    Suivant
                  </button>
                ) : (
                  <button onClick={() => setStep('subscription')} className={styles.submitBtn}>
                    Continuer
                  </button>
                )}
              </div>
            </div>
          )}

          {step === 'subscription' && (
            <div className={styles.subscriptionWrapper}>
              <div className={styles.headerText}>
                <h2>Passez à la vitesse supérieure</h2>
                <p>Choisissez un plan pour stocker vos photos en HD. (Optionnel)</p>
              </div>

              <div className={styles.plansGrid}>
                <div className={styles.planCard}>
                  <h3>Basic</h3>
                  <div className={styles.price}>Gratuit</div>
                  <ul>
                    <li><CheckCircle2 size={16}/> 100 Photos / mois</li>
                    <li><CheckCircle2 size={16}/> Commission 20%</li>
                  </ul>
                  <button onClick={handleFinish} className={styles.planBtnOutline}>Sélectionner</button>
                </div>
                
                <div className={`${styles.planCard} ${styles.planCardPro}`}>
                  <div className={styles.popularBadge}>Populaire</div>
                  <h3>Pro</h3>
                  <div className={styles.price}>10.000 FCFA<span>/mois</span></div>
                  <ul>
                    <li><CheckCircle2 size={16}/> 5.000 Photos / mois</li>
                    <li><CheckCircle2 size={16}/> Commission 10%</li>
                  </ul>
                  <button onClick={handleFinish} className={styles.planBtnFull}>Sélectionner</button>
                </div>
              </div>

              <button onClick={handleFinish} className={styles.skipBtn}>
                Plus tard, aller au tableau de bord
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}

export default Login
