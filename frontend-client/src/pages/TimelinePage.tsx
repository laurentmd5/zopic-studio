import { useNavigate } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import './TimelinePage.css'

export default function TimelinePage() {
  const navigate = useNavigate()

  // Mock data based on the provided mockup
  const timelineData = [
    {
      year: "2025",
      events: [
        {
          id: 1,
          day: "12",
          month: "Avril",
          title: "Marathon Dakar 2025",
          location: "Dakar, Sénégal",
          image: "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=100&q=80"
        },
        {
          id: 2,
          day: "22",
          month: "Févr.",
          title: "Semi-Marathon de Saint-Louis",
          location: "Saint-Louis, Sénégal",
          image: "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=100&q=80"
        },
        {
          id: 3,
          day: "5",
          month: "Janv.",
          title: "Dakar 10K",
          location: "Dakar, Sénégal",
          image: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=100&q=80"
        }
      ]
    },
    {
      year: "2024",
      events: [
        {
          id: 4,
          day: "10",
          month: "Nov.",
          title: "Course de la Paix",
          location: "Ziguinchor, Sénégal",
          image: "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=100&q=80"
        }
      ]
    }
  ]

  return (
    <div className="timeline-container">
      {/* Header */}
      <header className="timeline-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2 className="page-title">Ma Timeline</h2>
      </header>

      {/* Content */}
      <div className="timeline-content">
        {timelineData.map((group) => (
          <div key={group.year} className="timeline-year-group">
            <div className="timeline-year-label">{group.year}</div>
            
            <div className="timeline-events">
              {group.events.map((event) => (
                <div key={event.id} className="timeline-event-row">
                  <div className="timeline-event-date">
                    <span>{event.day}</span>
                    <span>{event.month}</span>
                  </div>
                  
                  <div className="timeline-event-card">
                    <div className="timeline-event-info">
                      <h3 className="timeline-event-title">{event.title}</h3>
                      <p className="timeline-event-location">{event.location}</p>
                    </div>
                    <img src={event.image} alt={event.title} className="timeline-event-image" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
