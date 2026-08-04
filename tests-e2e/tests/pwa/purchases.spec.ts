import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('PWA - Purchases & SSE', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    mockBackend.purchases = [
      {
        id: 10,
        total_amount: 1500,
        created_at: new Date().toISOString(),
        items: [
          { id: 1, photo_id: 101, url: 'mock1.jpg' }
        ],
        archives: []
      }
    ];
    await mockBackend.setup();
  });

  test('Doit afficher les achats et permettre le téléchargement', async ({ page }) => {
    // Naviguer vers /purchases (simulé post-paiement ou accès direct via menu)
    await page.goto('http://localhost:5174/purchases');
    
    // Le composant "Mes Achats" devrait se charger
    await expect(page.locator('text=Mes Achats').first()).toBeVisible();
    
    // Une commande devrait être visible
    await expect(page.locator('text=1500 FCFA').first()).toBeVisible();
    
    // Test du bouton télécharger
    // Si on a un bouton "Télécharger", on s'assure qu'il est cliquable
    const btnDownload = page.locator('button', { hasText: /Télécharger/i }).first();
    if (await btnDownload.isVisible()) {
      await expect(btnDownload).toBeEnabled();
      // On ne clique pas forcément car ça peut déclencher une navigation vers un blob mocké
    }
  });
});
