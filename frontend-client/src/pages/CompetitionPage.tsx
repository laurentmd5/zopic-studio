import { useNavigate, useParams } from 'react-router-dom'
import { Calendar, MapPin, Trophy } from 'lucide-react'

export default function CompetitionPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  // Simuler les données récupérées depuis l'API via competitionStore
  const competition = {
    name: "Marathon de Dakar 2026",
    date: "14 Février 2026",
    location: "Corniche Ouest, Dakar",
    sport: "Athlétisme",
    price: "1500 FCFA / photo"
  }

  return (
    <div className="container">
      <div className="header">
        <h1>{competition.name}</h1>
        <p>Revivez vos meilleurs moments sportifs</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Calendar size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.date}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <MapPin size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.location}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Trophy size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition.sport}</span>
        </div>
        <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          <p style={{ textAlign: 'center', fontWeight: 'bold' }}>Tarif unique : {competition.price}</p>
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <button className="btn btn-primary" onClick={() => navigate(`/competition/${id}/search`)}>
          🔍 Retrouver mes photos
        </button>
      </div>
    </div>
  )
}
