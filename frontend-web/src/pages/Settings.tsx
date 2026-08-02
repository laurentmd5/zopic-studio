import React, { useState } from 'react'
import { User, Phone, Save } from 'lucide-react'
import toast from 'react-hot-toast'
import styles from './Settings.module.css'

const Settings: React.FC = () => {
  const [profile, setProfile] = useState({
    name: 'Moussa Diop',
    bio: 'Photographe sportif basé à Dakar. Spécialiste Navétanes.',
    waveNumber: '771234567'
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setProfile(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Connecter à l'API PUT /auth/profile
    toast.success('Profil mis à jour avec succès !')
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Paramètres du Profil</h2>
        <p className={styles.subtitle}>Gérez vos informations publiques et vos paramètres de paiement.</p>
      </div>

      <div className={styles.content}>
        <form className={styles.form} onSubmit={handleSubmit}>
          
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <User size={20} className={styles.icon} />
              <h3>Informations Publiques</h3>
            </div>
            
            <div className={styles.inputGroup}>
              <label>Nom d'affichage</label>
              <input 
                type="text" 
                name="name"
                value={profile.name} 
                onChange={handleChange}
                placeholder="Votre nom de photographe" 
              />
            </div>
            
            <div className={styles.inputGroup}>
              <label>Biographie</label>
              <textarea 
                name="bio"
                value={profile.bio} 
                onChange={handleChange}
                rows={4}
                placeholder="Décrivez votre style et votre expérience..."
              ></textarea>
            </div>
          </div>

          <div className={styles.divider}></div>

          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <Phone size={20} className={styles.icon} />
              <h3>Paiement Mobile</h3>
            </div>
            <p className={styles.helpText}>
              Ce numéro sera utilisé pour vous reverser automatiquement vos gains (Wave ou Orange Money).
            </p>
            
            <div className={styles.inputGroup}>
              <label>Numéro de téléphone (Mobile Money)</label>
              <input 
                type="tel" 
                name="waveNumber"
                value={profile.waveNumber} 
                onChange={handleChange}
                placeholder="77 XXX XX XX" 
              />
            </div>
          </div>

          <div className={styles.actions}>
            <button type="submit" className={styles.saveBtn}>
              <Save size={18} />
              <span>Enregistrer les modifications</span>
            </button>
          </div>
          
        </form>
      </div>
    </div>
  )
}

export default Settings
