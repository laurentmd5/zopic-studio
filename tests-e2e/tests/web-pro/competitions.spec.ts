import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('Web Pro - Compétitions & Upload', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    mockBackend.currentUser = { id: 1, phone_number: '771234567', full_name: "Test" };
    await mockBackend.setup();

    await page.goto('http://localhost:5173/');
    await page.evaluate(() => { localStorage.setItem('auth_token', 'mock_token'); });
  });

  test('Doit pouvoir créer une compétition et gérer ses paramètres', async ({ page }) => {
    await page.goto('http://localhost:5173/competitions');
    
    await page.click('text=Nouvelle compétition');
    
    // Remplissage du formulaire
    await page.fill('input[placeholder="Ex: Marathon de Dakar"]', 'Marathon de Dakar E2E');
    await page.fill('input[type="date"]', '2026-10-10');
    await page.fill('input[placeholder="Ex: Corniche Ouest, Dakar"]', 'Dakar');
    
    // Si un select de sport est présent
    const sportSelect = page.locator('select').first();
    if (await sportSelect.isVisible()) {
      await sportSelect.selectOption({ index: 1 });
    }
    
    await page.fill('input[placeholder*="10km"]', '10km');
    
    // Prix
    await page.fill('input[type="number"]', '1500');
    
    await page.click('button:has-text("Créer")');
    
    // On clique sur la nouvelle compétition dans la liste
    await expect(page.locator('h3:has-text("Marathon de Dakar E2E")').first()).toBeVisible();
    await page.click('h3:has-text("Marathon de Dakar E2E")');
    
    // On devrait être redirigé vers la page de la compétition
    await expect(page.locator('h3:has-text("Marathon de Dakar E2E")').or(page.locator('h2:has-text("Marathon de Dakar E2E")'))).toBeVisible();
    
    // Aller dans les paramètres de la compétition (l'onglet)
    await page.locator('button:has-text("Paramètres")').click();
    
    // Vérification de l'ouverture du modal de paramètres
    await expect(page.locator('text=Paramètres de la compétition')).toBeVisible();
  });
});
