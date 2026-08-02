import React, { useState } from 'react'
import { X, ChevronLeft, ChevronRight, Save, Tag } from 'lucide-react'
import toast from 'react-hot-toast'
import styles from './PhotoLightbox.module.css'

interface Photo {
  id: number
  s3_object_key: string
  status: string
  // Additional mocked metadata for MVP
  bibNumber?: string 
}

interface PhotoLightboxProps {
  photos: Photo[]
  initialIndex: number
  onClose: () => void
  onUpdatePhoto?: (id: number, bibNumber: string) => void
}

const PhotoLightbox: React.FC<PhotoLightboxProps> = ({ photos, initialIndex, onClose, onUpdatePhoto }) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex)
  const [bibNumber, setBibNumber] = useState(photos[initialIndex]?.bibNumber || '')
  
  const currentPhoto = photos[currentIndex]

  if (!currentPhoto) return null

  const handleNext = () => {
    const nextIndex = (currentIndex + 1) % photos.length
    setCurrentIndex(nextIndex)
    setBibNumber(photos[nextIndex]?.bibNumber || '')
  }

  const handlePrev = () => {
    const prevIndex = (currentIndex - 1 + photos.length) % photos.length
    setCurrentIndex(prevIndex)
    setBibNumber(photos[prevIndex]?.bibNumber || '')
  }

  const handleSaveTag = (e: React.FormEvent) => {
    e.preventDefault()
    if (onUpdatePhoto) {
      onUpdatePhoto(currentPhoto.id, bibNumber)
    }
    toast.success('Dossard tagué avec succès !')
  }

  return (
    <div className={styles.overlay}>
      <button className={styles.closeBtn} onClick={onClose}>
        <X size={24} />
      </button>

      <div className={styles.content}>
        <div className={styles.imageContainer}>
          <button className={styles.navBtn} onClick={handlePrev}>
            <ChevronLeft size={36} />
          </button>
          
          <img 
            src={`https://placehold.co/1200x800/png?text=Photo+${currentPhoto.id}`} 
            alt={currentPhoto.s3_object_key} 
            className={styles.image}
          />

          <button className={styles.navBtn} onClick={handleNext}>
            <ChevronRight size={36} />
          </button>
        </div>

        <div className={styles.sidebar}>
          <h3>Détails de la photo</h3>
          
          <div className={styles.metaInfo}>
            <p><strong>Fichier:</strong> {currentPhoto.s3_object_key.split('/').pop()}</p>
            <p><strong>Statut IA:</strong> {currentPhoto.status}</p>
          </div>

          <div className={styles.tagSection}>
            <div className={styles.tagHeader}>
              <Tag size={18} />
              <h4>Tag Manuel (Dossard)</h4>
            </div>
            <p className={styles.tagDesc}>Forcer ou corriger le numéro de dossard détecté par l'IA.</p>
            
            <form onSubmit={handleSaveTag} className={styles.tagForm}>
              <input 
                type="text" 
                placeholder="Ex: 405" 
                value={bibNumber}
                onChange={(e) => setBibNumber(e.target.value)}
                className={styles.tagInput}
              />
              <button type="submit" className={styles.saveBtn}>
                <Save size={16} />
                <span>Enregistrer</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PhotoLightbox
