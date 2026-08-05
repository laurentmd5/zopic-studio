import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './AuthPage.css';

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [isLoginView, setIsLoginView] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      // Simulate login/register
      login();
      navigate('/');
    }
  };

  return (
    <div className="auth-container">
      <header className="auth-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
      </header>

      <div className="auth-content">
        <div className="auth-logo">
          <h1>Z<span>O</span>Pic</h1>
          <p>Studio</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLoginView && (
            <div className="auth-input-group">
              <label>Nom complet</label>
              <input type="text" placeholder="Ex: Moussa Diop" />
            </div>
          )}

          <div className="auth-input-group">
            <label>Email</label>
            <input 
              type="email" 
              placeholder="votre@email.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="auth-input-group">
            <label>Mot de passe</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-auth-submit">
            {isLoginView ? 'Se connecter' : "S'inscrire"}
          </button>

          <div className="auth-divider">OU</div>

          <button type="button" className="btn-auth-google">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google" width="18" height="18" />
            Continuer avec Google
          </button>
        </form>

        <div className="auth-footer">
          {isLoginView ? (
            <span>Nouveau sur ZoPic ? <span className="auth-link" onClick={() => setIsLoginView(false)}>Créer un compte</span></span>
          ) : (
            <span>Déjà un compte ? <span className="auth-link" onClick={() => setIsLoginView(true)}>Se connecter</span></span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
