import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Link as LinkIcon, Trash2, MonitorPlay, FileText } from 'lucide-react';
import './SharesPage.css';

interface ShareItem {
  id: number;
  title: string;
  url: string;
  type: 'youtube' | 'article' | 'link';
}

const SharesPage: React.FC = () => {
  const navigate = useNavigate();
  
  const [shares, setShares] = useState<ShareItem[]>([
    {
      id: 1,
      title: "Interview RTS Sport",
      url: "https://youtube.com/watch?v=...",
      type: 'youtube'
    },
    {
      id: 2,
      title: "Article L'Équipe : La révélation",
      url: "https://lequipe.fr/...",
      type: 'article'
    }
  ]);

  const [newTitle, setNewTitle] = useState('');
  const [newUrl, setNewUrl] = useState('');

  const handleAddShare = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newUrl) return;

    // Detect type simply based on URL for the prototype
    let type: 'youtube' | 'article' | 'link' = 'link';
    if (newUrl.includes('youtube.com') || newUrl.includes('youtu.be')) type = 'youtube';
    else if (newUrl.includes('lequipe') || newUrl.includes('news')) type = 'article';

    const newItem: ShareItem = {
      id: Date.now(),
      title: newTitle,
      url: newUrl,
      type
    };

    setShares([newItem, ...shares]);
    setNewTitle('');
    setNewUrl('');
  };

  const handleDelete = (id: number) => {
    setShares(shares.filter(s => s.id !== id));
  };

  const getIconForType = (type: string) => {
    switch (type) {
      case 'youtube': return <MonitorPlay size={20} color="#ef4444" />;
      case 'article': return <FileText size={20} color="#3b82f6" />;
      default: return <LinkIcon size={20} />;
    }
  };

  return (
    <div className="shares-manage-container">
      {/* Header */}
      <header className="shares-manage-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h2>Mes Partages</h2>
      </header>

      <div className="shares-manage-content">
        
        {/* Form Add */}
        <div className="share-add-card">
          <div className="share-add-title">Ajouter un nouveau lien</div>
          <form onSubmit={handleAddShare}>
            <div className="share-input-group">
              <input 
                type="text" 
                className="share-input" 
                placeholder="Titre du lien (ex: Mon interview)" 
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
              />
              <input 
                type="url" 
                className="share-input" 
                placeholder="URL (https://...)" 
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-add-share">Ajouter à mon profil</button>
          </form>
        </div>

        {/* List */}
        <h3 className="shares-list-title">Liens partagés ({shares.length})</h3>
        
        {shares.length === 0 ? (
          <div className="empty-shares">
            <LinkIcon size={48} className="empty-shares-icon" />
            <p>Vous n'avez pas encore partagé d'articles ou de vidéos.<br/>Ajoutez-les ici pour enrichir votre profil public !</p>
          </div>
        ) : (
          <div className="shares-list">
            {shares.map(share => (
              <div key={share.id} className="share-item-card">
                <div className="share-item-icon">
                  {getIconForType(share.type)}
                </div>
                <div className="share-item-info">
                  <div className="share-item-title">{share.title}</div>
                  <div className="share-item-url">{share.url}</div>
                </div>
                <button 
                  className="btn-delete-share"
                  onClick={() => handleDelete(share.id)}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default SharesPage;
