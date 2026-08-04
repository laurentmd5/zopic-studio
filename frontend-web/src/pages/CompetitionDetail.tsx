import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, UploadCloud, Settings, Trash2, Share2, Copy, Plus, FolderOpen } from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'
import toast from 'react-hot-toast'
import { competitionsService, storageService } from '../services/competitionsService'
import PhotoLightbox from '../components/common/PhotoLightbox'
import styles from './CompetitionDetail.module.css'

const CompetitionDetail: React.FC = () => {
  const { competitionId } = useParams<{ competitionId: string }>()
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
  
  // Settings Modal State
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [packsEnabled, setPacksEnabled] = useState(false)
  const [packsConfig, setPacksConfig] = useState<any[]>([])

  useEffect(() => {
    if (competitionId) {
      fetchEventDetails()
    }
  }, [competitionId])

  const fetchEventDetails = async () => {
    try {
      setLoading(true)
      const data = await competitionsService.getEventDetails(competitionId!)
      setEvent(data)
      setPacksEnabled(data.packs_enabled || false)
      setPacksConfig(data.packs || [])
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

  const handleSaveSettings = async () => {
    try {
      await toast.promise(
        competitionsService.updateCompetitionPacks(competition.id, packsEnabled, packsConfig),
        {
          loading: 'Sauvegarde des paramètres...',
          success: 'Paramètres mis à jour',
          error: 'Erreur de sauvegarde'
        }
      )
      setShowSettingsModal(false)
      fetchEventDetails()
    } catch (err) {
      console.error(err)
    }
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
          <button className={styles.secondaryBtn} onClick={() => setShowSettingsModal(true)}>
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

      {showSettingsModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal} style={{ maxWidth: '600px' }}>
            <div className={styles.modalHeader}>
              <h3>Paramètres de la compétition</h3>
              <button className={styles.closeBtn} onClick={() => setShowSettingsModal(false)}>×</button>
            </div>
            
            <div className={styles.publishContent}>
              <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{ fontWeight: 'bold' }}>Activer les Packs de photos</label>
                <input 
                  type="checkbox" 
                  checked={packsEnabled} 
                  onChange={(e) => setPacksEnabled(e.target.checked)}
                  style={{ width: '20px', height: '20px' }}
                />
              </div>

              {packsEnabled && (
                <div>
                  <h4 style={{ marginBottom: '1rem' }}>Configuration des Packs</h4>
                  {packsConfig.map((pack, index) => (
                    <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px', alignItems: 'center' }}>
                      <input 
                        type="number" 
                        placeholder="Quantité (ex: 5)" 
                        value={pack.quantity}
                        onChange={(e) => {
                          const newConfig = [...packsConfig]
                          newConfig[index].quantity = parseInt(e.target.value) || 0
                          setPacksConfig(newConfig)
                        }}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', flex: 1 }}
                      />
                      <input 
                        type="number" 
                        placeholder="Prix XOF (ex: 2000)" 
                        value={pack.price_xof}
                        onChange={(e) => {
                          const newConfig = [...packsConfig]
                          newConfig[index].price_xof = parseInt(e.target.value) || 0
                          setPacksConfig(newConfig)
                        }}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', flex: 1 }}
                      />
                      <input 
                        type="text" 
                        placeholder="Label (ex: 5 photos)" 
                        value={pack.label}
                        onChange={(e) => {
                          const newConfig = [...packsConfig]
                          newConfig[index].label = e.target.value
                          setPacksConfig(newConfig)
                        }}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', flex: 1 }}
                      />
                      <button 
                        onClick={() => {
                          const newConfig = packsConfig.filter((_, i) => i !== index)
                          setPacksConfig(newConfig)
                        }}
                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))}
                  <button 
                    onClick={() => setPacksConfig([...packsConfig, { quantity: 0, price_xof: 0, label: '' }])}
                    className={styles.secondaryBtn}
                    style={{ marginTop: '10px' }}
                  >
                    <Plus size={16} /> Ajouter un pack
                  </button>
                </div>
              )}
            </div>
            
            <div className={styles.modalActions}>
              <button type="button" className={styles.secondaryBtn} onClick={() => setShowSettingsModal(false)}>Annuler</button>
              <button type="button" className={styles.primaryBtn} onClick={handleSaveSettings}>Sauvegarder</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CompetitionDetail
