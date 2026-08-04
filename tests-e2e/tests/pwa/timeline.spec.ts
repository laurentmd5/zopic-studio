import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('PWA - Timeline Sportive', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    await mockBackend.setup();

    // Set guest session ID
    await page.addInitScript(() => {
      window.localStorage.setItem('x_session_id', 'guest-123');
    });
  });

  test('Doit afficher la timeline correctement avec les icônes et formats de date', async ({ page }) => {
    await page.goto('http://localhost:5174/timeline');
    
    // Attendre que la page se charge
    await expect(page.locator('h1:has-text("ZoPic Photos")')).toBeVisible();

    // Vérifier le message et stats
    await expect(page.locator('text=Le début d\'une grande aventure')).toBeVisible();
    await expect(page.locator('text=2 compétitions')).toBeVisible();
    await expect(page.locator('text=20 photos')).toBeVisible();

    // Vérifier le regroupement par année (2026 déplié par défaut)
    await expect(page.locator('text=── 2026 ──')).toBeVisible();

    // Vérifier la présence des 2 cartes avec les bons formats
    const navetanesCard = page.locator('.card:has-text("Finale Navétanes Pikine")');
    await expect(navetanesCard).toBeVisible();
    await expect(navetanesCard.locator('text=15 août 2026')).toBeVisible();
    await expect(navetanesCard.locator('text=⚽')).toBeVisible();
    await expect(navetanesCard.locator('text=📸 12')).toBeVisible();

    const marathonCard = page.locator('.card:has-text("Marathon Dakar")');
    await expect(marathonCard).toBeVisible();
    await expect(marathonCard.locator('text=22 juillet 2026')).toBeVisible();
    await expect(marathonCard.locator('text=🏃')).toBeVisible();
    await expect(marathonCard.locator('text=📸 8')).toBeVisible();
  });

  test('Doit rediriger vers la compétition au clic sur la carte', async ({ page }) => {
    await page.goto('http://localhost:5174/timeline');
    
    // Attendre le chargement
    await expect(page.locator('text=── 2026 ──')).toBeVisible();

    // Clic sur la carte Navétanes (id = 1)
    const navetanesCard = page.locator('.card:has-text("Finale Navétanes Pikine")');
    await navetanesCard.click();

    // Vérifier la redirection
    await expect(page).toHaveURL(/.*\/competition\/1.*/);
  });
});
