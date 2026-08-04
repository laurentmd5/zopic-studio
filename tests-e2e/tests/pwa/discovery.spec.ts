import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('PWA - Discovery & Recherche', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    await mockBackend.setup();
  });

  test('Accéder à une compétition et faire une recherche Tout', async ({ page }) => {
    await page.goto('http://localhost:5174/competition/999');
    
    // Le nom de la compétition (du mock) doit être visible
    await expect(page.locator('text=Marathon E2E').first()).toBeVisible();
    
    await page.locator('.btn-primary').first().click();
    
    // Test recherche "Tout"
    await page.click('text=Tout');
    
    // Les photos mockées (3 photos) devraient s'afficher
    await expect(page.locator('.photo-card')).toHaveCount(3, { timeout: 10000 });
  });

  test('Recherche par selfie (Face Recognition Mock)', async ({ page }) => {
    await page.goto('http://localhost:5174/competition/999');
    await page.click('button:has-text("Retrouver mes photos")');
    
    // Sélectionne Selfie
    await page.click('text=Selfie');
    
    // Simuler l'upload d'un selfie en utilisant setInputFiles sur l'input hidden
    // On utilise un fichier arbitraire juste pour déclencher l'événement change
    await page.locator('input[type="file"]').setInputFiles('package.json');
    
    // La recherche se lance automatiquement (Loading)
    await expect(page.locator('text=Analyse IA en cours')).toBeVisible();

    // En mock API, le POST /search/competitions/999 va juste renvoyer 3 photos
    await expect(page.locator('.photo-card')).toHaveCount(3, { timeout: 10000 });
  });
});
