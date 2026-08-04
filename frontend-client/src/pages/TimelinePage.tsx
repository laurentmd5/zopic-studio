import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ChevronDown, ChevronRight, RefreshCcw, Camera, MapPin, Calendar as CalendarIcon } from 'lucide-react'
import { useTimelineStore } from '../store/timelineStore'

const sportIcons: Record<string, string> = {
  football: '⚽',
  basketball: '🏀',
  lutte: '🤼',
  athletisme: '🏃',
  cyclisme: '🚴',
  volleyball: '🏐',
  tennis: '🎾',
  arts_martiaux: '🥋',
  natation: '🏊',
}

const getSportIcon = (sport: string) => sportIcons[sport?.toLowerCase()] || '🏆'

const formatDate = (dateString: string) => {
  try {
    return new Intl.DateTimeFormat('fr-FR', { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    }).format(new Date(dateString))
  } catch (e) {
    return dateString
  }
}

export default function TimelinePage() {
  const navigate = useNavigate()
  const { 
    timeline, 
    totalCompetitions, 
    totalPhotos, 
    message, 
    isLoading, 
    error, 
    expandedYears, 
    fetchTimeline, 
    toggleYear 
  } = useTimelineStore()

  useEffect(() => {
    fetchTimeline()
  }, [fetchTimeline])

  if (isLoading && timeline.length === 0) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#3A4B29] border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (error && timeline.length === 0) {
    return (
      <div className="min-h-screen bg-white p-6 flex flex-col items-center justify-center text-center">
        <h3 className="text-xl font-bold text-red-500 mb-2">Erreur</h3>
        <p className="text-gray-600 mb-6">{error}</p>
        <button className="btn-outline px-6 py-2 rounded-xl flex items-center gap-2" onClick={() => fetchTimeline()}>
          <RefreshCcw size={16} /> Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-32">
      {/* Header */}
      <div className="bg-white px-6 pt-8 pb-4 border-b border-gray-100 shadow-sm sticky top-0 z-40 flex items-center">
        <button onClick={() => navigate(-1)} className="text-gray-900">
          <ArrowLeft size={24} />
        </button>
        <h2 className="ml-4 text-2xl font-bold text-gray-900">Ma Carrière</h2>
      </div>

      {timeline.length === 0 ? (
        <div className="p-6 mt-10 flex flex-col items-center text-center">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
            <Camera size={32} className="text-gray-400" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Aucune compétition</h3>
          <p className="text-gray-500 mb-8">
            Retrouvez vos photos lors de votre prochain événement sportif !
          </p>
          <button className="bg-[#3A4B29] text-white font-bold w-full py-4 rounded-xl shadow-md" onClick={() => navigate('/')}>
            Trouver mes photos
          </button>
        </div>
      ) : (
        <div className="p-6">
          <div className="text-center mb-8">
            <h2 className="text-[#3A4B29] font-bold text-xl mb-1">
              {message || "Votre carrière sportive en images 🏆"}
            </h2>
            <p className="text-gray-500 text-sm font-medium">
              {totalCompetitions} compétition{totalCompetitions > 1 ? 's' : ''} • {totalPhotos} photo{totalPhotos > 1 ? 's' : ''}
            </p>
          </div>

          <div className="relative pl-6">
            {/* Ligne verticale de la timeline */}
            <div className="absolute left-[11px] top-2 bottom-0 w-0.5 bg-gray-200"></div>
            
            {timeline.map((group) => {
              const isExpanded = expandedYears.includes(group.year)
              
              return (
                <div key={group.year} className="mb-8 relative">
                  {/* Point sur la ligne pour l'année */}
                  <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#3A4B29] border-4 border-gray-50 z-10"></div>
                  
                  <div 
                    onClick={() => toggleYear(group.year)}
                    className="flex items-center cursor-pointer mb-4 select-none"
                  >
                    <h3 className="m-0 mr-2 text-xl font-bold text-gray-900">{group.year}</h3>
                    <div className="text-gray-400">
                      {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="flex flex-col gap-4 mt-4">
                      {group.competitions.map((comp) => (
                        <div 
                          key={comp.id} 
                          onClick={() => navigate(`/competition/${comp.id}`)}
                          className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100 cursor-pointer transition-transform active:scale-[0.98]"
                        >
                          <div className="h-32 bg-gray-200 relative">
                            {comp.cover_photo_url ? (
                              <img src={comp.cover_photo_url} alt={comp.name} className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <Camera size={32} className="text-gray-400 opacity-50" />
                              </div>
                            )}
                            <div className="absolute top-2 right-2 bg-black/60 text-white backdrop-blur-sm px-2 py-1 rounded text-xs font-bold flex items-center gap-1">
                              <Camera size={12} /> {comp.photos_count}
                            </div>
                          </div>
                          <div className="p-4">
                            <div className="text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
                              <CalendarIcon size={12} /> {formatDate(comp.date)}
                            </div>
                            <h4 className="font-bold text-gray-900 text-lg mb-1 leading-tight">
                              {getSportIcon(comp.sport)} {comp.name}
                            </h4>
                            <div className="text-xs text-gray-500 flex items-center gap-1">
                              <MapPin size={12} /> {comp.location}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
