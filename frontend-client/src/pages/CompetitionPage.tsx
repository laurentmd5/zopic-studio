import { useNavigate, useParams } from 'react-router-dom'
import { Calendar, MapPin, Trophy } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function CompetitionPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const [competition, setCompetition] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCompetition = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/competitions/${id}`);
        if (response.ok) {
          const data = await response.json();
          setCompetition(data);
        } else {
          // Fallback to mock data if API fails (for local testing without backend)
          setCompetition({
            name: "Marathon de Dakar 2026",
            date: "14 Février 2026",
            location: "Corniche Ouest, Dakar",
            sport: "Athlétisme",
            price: "1500 FCFA / photo"
          });
        }
      } catch (error) {
        setCompetition({
          name: "Marathon de Dakar 2026",
          date: "14 Février 2026",
          location: "Corniche Ouest, Dakar",
          sport: "Athlétisme",
          price: "1500 FCFA / photo"
        });
      } finally {
        setLoading(false);
      }
    };
    fetchCompetition();
  }, [id]);

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="container">
      <div className="header">
        <h1>{competition?.name}</h1>
        <p>Revivez vos meilleurs moments sportifs</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Calendar size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition?.date}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <MapPin size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition?.location || 'Dakar'}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <Trophy size={20} style={{ marginRight: '10px', color: 'var(--color-accent)' }} />
          <span>{competition?.sport || 'Running'}</span>
        </div>
        <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          <p style={{ textAlign: 'center', fontWeight: 'bold' }}>Tarif unique : {competition?.settings?.price_per_photo || '1500'} FCFA / photo</p>
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
