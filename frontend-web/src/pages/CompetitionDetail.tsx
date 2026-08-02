import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, UploadCloud, Settings, Trash2, Share2, Copy, Plus, FolderOpen } from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'
import toast from 'react-hot-toast'
import { competitionsService, storageService } from '../services/competitionsService'
import PhotoLightbox from '../components/common/PhotoLightbox'
import styles from './CompetitionDetail.module.css'

const CompetitionDetail: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>()
  const [competition, setEvent] = useState<any>(null)
  const [photos, setPhotos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  
  // Publish Modal State
  const [showPublishModal, setShowPublishModal] = useState(false)

  // Lightbox State
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null)

  useEffect(() => {
    if (eventId) {
      fetchEventDetails()
    }
  }, [eventId])

  const fetchEventDetails = async () => {
    try {
      setLoading(true)
      const data = await competitionsService.getEventDetails(eventId!)
      setEvent(data)
      const allPhotos = data.epreuves?.flatMap((a: any) => a.photos) || []
      setPhotos(allPhotos)
    } catch (error) {
      console.error('Error fetching competition details', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true)
    } else if (e.type === 'dragleave') {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesUpload(Array.from(e.dataTransfer.files))
    }
  }, [competition])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesUpload(Array.from(e.target.files))
    }
  }

  const handleFilesUpload = async (files: File[]) => {
    if (!competition || files.length === 0) return
    
    setUploading(true)
    setProgress(0)

    try {
      // 1. Get or create epreuve
      let albumId = null
      if (competition.epreuves && competition.epreuves.length > 0) {
        albumId = competition.epreuves[0].id
      } else {
        const newÉpreuve = await competitionsService.createÉpreuve(competition.id, 'Général')
        albumId = newÉpreuve.id
      }

      // 2. Upload files
      let completed = 0
      for (const file of files) {
        // a. Request Upload URL
        const uploadData = await storageService.getUploadUrl(file.name, file.type)
        
        // b. Direct PUT to Storage
        await storageService.uploadToUrl(uploadData.upload_url, file)
        
        // c. Save Photo to DB
        await competitionsService.addPhotoToÉpreuve(albumId, uploadData.object_key)

        completed++
        setProgress(Math.round((completed / files.length) * 100))
      }

      // 3. Refresh data
      await fetchEventDetails()
    } catch (error) {
      console.error('Error during upload', error)
      toast.error('Une erreur est survenue lors du téléversement.')
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  const handlePublish = async () => {
    // Mock API call to update status
    toast.promise(
      new Promise(resolve => setTimeout(resolve, 1000)),
      {
        loading: 'Publication en cours...',
        success: 'Compétition publié avec succès !',
        error: 'Erreur lors de la publication',
      }
    ).then(() => {
      setEvent({ ...competition, status: 'Publié' })
      setShowPublishModal(true)
    })
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Lien copié dans le presse-papiers !')
  }

  if (loading || !competition) {
    return <div className={styles.container}><p>Chargement des détails de la compétition...</p></div>
  }


  const publicLink = `https://zopic.studio/e/${competition.id}`

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <Link to="/competitions" className={styles.backBtn}>
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h2 className={styles.title}>{competition.name}</h2>
            <div className={styles.meta}>
              <span className={styles.badge}>{competition.status || 'Brouillon'}</span>
              <span>{new Date(competition.date).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        
        <div className={styles.actions}>
          <button className={styles.secondaryBtn}>
            <Settings size={18} />
            <span>Paramètres</span>
          </button>
          {competition.status !== 'Publié' ? (
            <button className={styles.primaryBtn} onClick={handlePublish}>
              Publier la compétition
            </button>
          ) : (
            <button className={styles.primaryBtn} onClick={() => setShowPublishModal(true)}>
              <Share2 size={18} />
              Partager
            </button>
          )}
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.albumSidebar}>
          <div className={styles.albumHeader}>
            <h3>Épreuves</h3>
            <button className={styles.iconBtn} title="Nouvel epreuve">
              <Plus size={18} />
            </button>
          </div>
          <ul className={styles.albumList}>
            <li className={styles.albumItemActive}>
              <FolderOpen size={16} className={styles.albumIcon} />
              <span>Général</span>
              <span className={styles.albumCount}>{photos.length}</span>
            </li>
            {/* Simulation of other epreuves for MVP */}
            <li className={styles.albumItem}>
              <FolderOpen size={16} className={styles.albumIcon} />
              <span>Remise des prix</span>
              <span className={styles.albumCount}>0</span>
            </li>
            <li className={styles.albumItem}>
              <FolderOpen size={16} className={styles.albumIcon} />
              <span>Ambiance</span>
              <span className={styles.albumCount}>0</span>
            </li>
          </ul>
        </div>

        <div className={styles.mainExplorer}>
          {/* Dropzone */}
          <div 
            className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <UploadCloud size={48} className={styles.uploadIcon} />
            <h3>Glissez et déposez vos photos ici</h3>
            <p>ou</p>
            <label className={styles.browseBtn}>
              Parcourir les fichiers
              <input 
                type="file" 
                multiple 
                accept="image/jpeg, image/png, image/raw" 
                className={styles.fileInput}
                onChange={handleFileInput}
              />
            </label>
            <p className={styles.limits}>Supporte JPEG, PNG, RAW. Max 50MB par fichier.</p>
          </div>

          {uploading && (
            <div className={styles.uploadProgress}>
              <div className={styles.progressHeader}>
                <span>Upload en cours...</span>
                <span>{progress}%</span>
              </div>
              <div className={styles.progressBar}>
                <div className={styles.progressFill} style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

          {/* Gallery */}
          <div className={styles.gallerySection}>
            <div className={styles.galleryHeader}>
              <h3>Photos - Général ({photos.length})</h3>
              <button className={styles.textBtn}>Tout sélectionner</button>
            </div>
            
            <div className={styles.grid}>
              {photos.map((photo: any, index: number) => (
                <div key={photo.id} className={styles.photoCard}>
                  <div className={styles.photoWrapper} onClick={() => setLightboxIndex(index)}>
                    {/* Using a placeholder for now since we don't have public URLs from backend yet */}
                    <img src={`https://placehold.co/300x200/png?text=Photo+${photo.id}`} alt={photo.s3_object_key} loading="lazy" style={{cursor: 'pointer'}} />
                    <div className={styles.photoOverlay} onClick={(e) => e.stopPropagation()}>
                      <button className={styles.deleteBtn} title="Supprimer" onClick={() => toast.success('Photo supprimée (Simulation)')}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <div className={styles.photoInfo}>
                    <span className={styles.photoName} title={photo.s3_object_key}>{photo.s3_object_key.split('/').pop()}</span>
                    <span className={styles.photoSize}>Status: {photo.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {lightboxIndex !== null && (
        <PhotoLightbox 
          photos={photos} 
          initialIndex={lightboxIndex} 
          onClose={() => setLightboxIndex(null)}
          onUpdatePhoto={(id, bib) => {
            // Update local state to reflect the tag for MVP
            console.log(`Update photo ${id} with bib ${bib}`)
          }}
        />
      )}

      {showPublishModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3>Compétition Publié !</h3>
              <button className={styles.closeBtn} onClick={() => setShowPublishModal(false)}>×</button>
            </div>
            
            <div className={styles.publishContent}>
              <p>Votre compétition est maintenant accessible aux sportifs. Partagez ce QR Code ou le lien ci-dessous :</p>
              
              <div className={styles.qrContainer}>
                <QRCodeSVG value={publicLink} size={150} />
              </div>
              
              <div className={styles.linkContainer}>
                <input type="text" readOnly value={publicLink} className={styles.linkInput} />
                <button className={styles.copyBtn} onClick={() => copyToClipboard(publicLink)}>
                  <Copy size={18} />
                </button>
              </div>
            </div>
            
            <div className={styles.modalActions}>
              <button type="button" className={styles.primaryBtn} style={{width: '100%'}} onClick={() => setShowPublishModal(false)}>Fermer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CompetitionDetail
