import React from 'react'
import { TrendingUp, Image as ImageIcon, CreditCard, HardDrive } from 'lucide-react'
import styles from './Dashboard.module.css'

const Dashboard: React.FC = () => {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Vue d'ensemble</h2>
      
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statHeader}>
            <h3>Revenus du mois</h3>
            <div className={`${styles.iconWrapper} ${styles.green}`}>
              <TrendingUp size={20} />
            </div>
          </div>
          <div className={styles.statValue}>145 000 FCFA</div>
          <div className={styles.statTrend}>+12% par rapport au mois dernier</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statHeader}>
            <h3>Photos vendues</h3>
            <div className={`${styles.iconWrapper} ${styles.blue}`}>
              <ImageIcon size={20} />
            </div>
          </div>
          <div className={styles.statValue}>324</div>
          <div className={styles.statTrend}>Ce mois-ci</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statHeader}>
            <h3>Solde disponible</h3>
            <div className={`${styles.iconWrapper} ${styles.orange}`}>
              <CreditCard size={20} />
            </div>
          </div>
          <div className={styles.statValue}>45 000 FCFA</div>
          <button className={styles.actionBtn}>Retirer vers Wave</button>
        </div>
      </div>

      <div className={styles.mainSection}>
        <div className={styles.storageCard}>
          <div className={styles.storageHeader}>
            <h3>Stockage Cloud</h3>
            <HardDrive size={24} className={styles.storageIcon} />
          </div>
          
          <div className={styles.storageVisual}>
            {/* Simple CSS Circle logic or a bar for now */}
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: '22%' }}></div>
            </div>
          </div>
          
          <div className={styles.storageDetails}>
            <p><strong>45 Go</strong> utilisés sur 200 Go (Plan Starter)</p>
            <span className={styles.storageWarning}>Reste 155 Go</span>
          </div>
          
          <button className={styles.upgradeBtn}>Mettre à niveau (Pro - 1 To)</button>
        </div>

        <div className={styles.recentEvents}>
          <h3>Compétitions Récents</h3>
          <div className={styles.emptyState}>
            <p>Aucun compétition publié récemment.</p>
            <button className={styles.createBtn}>Créer un compétition</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
