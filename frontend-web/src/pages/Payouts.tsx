import React from 'react'
import { ArrowUpRight, ArrowDownRight, Clock, CheckCircle } from 'lucide-react'
import styles from './Payouts.module.css'

const Payouts: React.FC = () => {
  // Simulated data for MVP
  const transactions = [
    { id: 'TX-1004', type: 'withdraw', amount: -45000, date: '2026-08-01', status: 'pending', method: 'Wave' },
    { id: 'TX-1003', type: 'sale', amount: 12000, date: '2026-07-28', status: 'completed', competition: 'Marathon de Dakar' },
    { id: 'TX-1002', type: 'sale', amount: 33000, date: '2026-07-26', status: 'completed', competition: 'Finale Navétanes' },
    { id: 'TX-1001', type: 'withdraw', amount: -100000, date: '2026-07-15', status: 'completed', method: 'Orange Money' },
  ]

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Rétrocessions & Portefeuille</h2>
      
      <div className={styles.walletCards}>
        <div className={styles.balanceCard}>
          <h3>Solde Disponible</h3>
          <div className={styles.balanceAmount}>45 000 FCFA</div>
          <button className={styles.withdrawBtn}>Retirer les fonds</button>
        </div>

        <div className={styles.statsCard}>
          <div className={styles.statRow}>
            <span>Revenus totaux générés</span>
            <span className={styles.statValue}>190 000 FCFA</span>
          </div>
          <div className={styles.statRow}>
            <span>Total retiré</span>
            <span className={styles.statValue}>145 000 FCFA</span>
          </div>
        </div>
      </div>

      <div className={styles.transactionsSection}>
        <h3>Historique des Transactions</h3>
        
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Transaction</th>
                <th>Date</th>
                <th>Montant</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => (
                <tr key={tx.id}>
                  <td>
                    <div className={styles.txInfo}>
                      <div className={`${styles.txIcon} ${tx.type === 'sale' ? styles.iconGreen : styles.iconOrange}`}>
                        {tx.type === 'sale' ? <ArrowDownRight size={18} /> : <ArrowUpRight size={18} />}
                      </div>
                      <div>
                        <div className={styles.txTitle}>
                          {tx.type === 'sale' ? 'Vente de photos' : 'Retrait vers ' + tx.method}
                        </div>
                        <div className={styles.txSubtitle}>
                          {tx.competition || tx.id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className={styles.txDate}>{new Date(tx.date).toLocaleDateString()}</td>
                  <td className={`${styles.txAmount} ${tx.type === 'sale' ? styles.textGreen : ''}`}>
                    {tx.type === 'sale' ? '+' : ''}{tx.amount.toLocaleString()} FCFA
                  </td>
                  <td>
                    <div className={`${styles.badge} ${tx.status === 'completed' ? styles.badgeSuccess : styles.badgeWarning}`}>
                      {tx.status === 'completed' ? <CheckCircle size={14} /> : <Clock size={14} />}
                      <span>{tx.status === 'completed' ? 'Terminé' : 'En attente'}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Payouts
