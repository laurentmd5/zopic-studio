import { useNavigate, useParams } from 'react-router-dom'


export default function CompetitionPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  
  // Fake Hero Image URL, idealment provenant de competition.cover_photo
  const heroImageUrl = "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?auto=format&fit=crop&q=80&w=1000";

  return (
    <div className="min-h-screen bg-white pb-20 flex flex-col">
      {/* Header Logo */}
      <div className="pt-8 px-6 pb-4">
        <div className="flex items-center gap-2">
          <div className="text-3xl font-bold text-gray-900 tracking-tight">Zo<span className="text-[#3A4B29]">Pic</span></div>
        </div>
        <div className="text-[10px] font-bold text-[#3A4B29] tracking-widest uppercase ml-1">Studio</div>
      </div>

      {/* Main Copy */}
      <div className="px-6 pt-4 pb-8 z-10 bg-white">
        <h1 className="text-4xl font-bold text-gray-900 leading-tight mb-4">
          Vos meilleurs moments sportifs en images
        </h1>
        <p className="text-lg text-gray-600">
          Retrouvez, achetez et téléchargez vos photos de compétition
        </p>
      </div>

      {/* Hero Image (Athlete in action) */}
      <div className="relative flex-1 w-full min-h-[40vh] bg-black">
        <img 
          src={heroImageUrl} 
          alt="Athlete" 
          className="absolute inset-0 w-full h-full object-cover opacity-70"
          style={{ objectPosition: 'center 30%' }}
        />
        {/* Gradient Overlay from top to blend with white background */}
        <div className="absolute inset-0 bg-gradient-to-b from-white via-transparent to-black/60"></div>
        
        {/* CTAs positioned over the dark bottom part of the image */}
        <div className="absolute bottom-8 left-0 right-0 px-6 flex flex-col gap-4 z-20">
          <button 
            className="w-full py-4 bg-[#3A4B29] text-white font-bold rounded-xl text-lg shadow-lg"
            onClick={() => navigate(`/competition/${id}/search`)}
          >
            Trouver mes photos
          </button>
          
          <button 
            className="w-full py-4 bg-white/10 backdrop-blur-sm border-2 border-white text-white font-bold rounded-xl text-lg hover:bg-white/20 transition"
            onClick={() => navigate(`/identity/activate`)}
          >
            Se connecter / S'inscrire
          </button>
        </div>
      </div>
    </div>
  )
}
