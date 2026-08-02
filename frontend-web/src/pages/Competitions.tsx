import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Folder, MoreVertical, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'
import { competitionsService } from '../services/competitionsService'
import styles from './Competitions.module.css'

const Events: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [competitions, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  // Form states
  const [eventName, setEventName] = useState('')
  const [eventDate, setEventDate] = useState('')
  const [eventPrice, setEventPrice] = useState('500')
  const [eventLocation, setEventLocation] = useState('')
  const [eventSport, setEventSport] = useState('')
  const [eventCategories, setEventCategories] = useState('')

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      setLoading(true)
      const data = await competitionsService.getEvents()
      setEvents(data)
    } catch (error) {
      console.error('Error fetching competitions:', error)
      toast.error('Erreur lors du chargement des compétitions')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const settings = {
      location: eventLocation,
      sport: eventSport,
      categories: eventCategories.split(',').map(c => c.trim()),
      price_per_photo: parseInt(eventPrice)
    }
    
    toast.promise(
      competitionsService.createEvent({
        name: eventName,
        date: new Date(eventDate).toISOString(),
        settings: settings
      }),
      {
        loading: 'Création en cours...',
        success: 'Compétition créé avec succès !',
        error: 'Erreur lors de la création'
      }
    ).then(() => {
      setShowCreateModal(false)
      fetchEvents()
    })
  }

  const displayEvents = competitions.filter(evt => 
    evt.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Compétitions Sportifs</h2>
          <p className={styles.subtitle}>Gérez vos epreuves et publiez vos photos.</p>
        </div>
        <button className={styles.primaryBtn} onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          <span>Nouvel compétition</span>
        </button>
      </div>

      <div className={styles.controls}>
        <div className={styles.searchBar}>
          <Search size={18} className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Rechercher un compétition..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className={styles.filters}>
          <select className={styles.select}>
            <option value="all">Tous les statuts</option>
            <option value="published">Publiés</option>
            <option value="draft">Brouillons</option>
          </select>
        </div>
      </div>

      <div className={styles.grid}>
        {loading ? (
          <p>Chargement des compétitions...</p>
        ) : displayEvents.length === 0 ? (
          <p>Aucun compétition trouvé.</p>
        ) : (
          displayEvents.map((evt) => (
            <Link to={`/competitions/${evt.id}`} key={evt.id} className={styles.cardLink}>
              <div className={styles.card}>
                <div className={styles.cardCover}>
                  <div className={`${styles.badge} ${styles[(evt.status || 'brouillon').toLowerCase()]}`}>
                    {evt.status || 'Brouillon'}
                  </div>
                </div>
                <div className={styles.cardBody}>
                  <div className={styles.cardHeader}>
                    <h3>{evt.name}</h3>
                    <button className={styles.iconBtn} onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}><MoreVertical size={18} /></button>
                  </div>
                  <div className={styles.cardMeta}>
                    <div className={styles.metaItem}>
                      <Calendar size={16} />
                      <span>{new Date(evt.date).toLocaleDateString()}</span>
                    </div>
                    <div className={styles.metaItem}>
                      <Folder size={16} />
                      <span>{evt.photos_count || 0} photos</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {showCreateModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3>Créer un compétition</h3>
              <button className={styles.closeBtn} onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form className={styles.modalForm} onSubmit={handleCreate}>
              <div className={styles.inputGroup}>
                <label>Nom de l'compétition</label>
                <input 
                  type="text" 
                  required
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="Ex: Marathon de Dakar" 
                />
              </div>
              
              <div className={styles.inputGroup}>
                <label>Date</label>
                <input 
                  type="date" 
                  required
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                />
              </div>

              <div className={styles.inputGroup}>
                <label>Lieu</label>
                <input 
                  type="text" 
                  value={eventLocation}
                  onChange={(e) => setEventLocation(e.target.value)}
                  placeholder="Ex: Corniche Ouest, Dakar" 
                />
              </div>

              <div className={styles.inputGroup}>
                <label>Sport</label>
                <select 
                  value={eventSport}
                  onChange={(e) => setEventSport(e.target.value)}
                >
                  <option value="">Sélectionnez un sport</option>
                  <option value="Running">Running / Marathon</option>
                  <option value="Football">Football / Navétanes</option>
                  <option value="Lutte">Lutte Sénégalaise</option>
                  <option value="Basketball">Basketball</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>

              <div className={styles.inputGroup}>
                <label>Catégories (séparées par une virgule)</label>
                <input 
                  type="text" 
                  value={eventCategories}
                  onChange={(e) => setEventCategories(e.target.value)}
                  placeholder="Ex: 10km, Semi-Marathon, Élite" 
                />
              </div>
              
              <div className={styles.inputGroup}>
                <label>Prix par photo (FCFA)</label>
                <input 
                  type="number" 
                  required
                  min="200"
                  step="100"
                  value={eventPrice}
                  onChange={(e) => setEventPrice(e.target.value)}
                />
              </div>
              
              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setShowCreateModal(false)}>Annuler</button>
                <button type="submit" className={styles.primaryBtn}>Créer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Events
