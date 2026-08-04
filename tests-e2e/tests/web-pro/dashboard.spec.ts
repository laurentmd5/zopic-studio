import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('Web Pro - Dashboard & Abonnements', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    
    // Simuler un utilisateur déjà connecté
    mockBackend.currentUser = {
      id: 1,
      phone_number: '771234567',
      full_name: "Babacar Diop",
      role: "photographer",
      studio_name: "Test Studio",
      city: "Dakar"
    };
    
    await mockBackend.setup();

    // Ajouter un token dans le localStorage pour bypasser le login
    await page.goto('http://localhost:5173/');
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'mock_token');
    });
  });

  test('Afficher dashboard et offre abo', async ({ page }) => {
    await page.goto('http://localhost:5173/dashboard');
    
    await expect(page.locator('text=Vue d\'ensemble')).toBeVisible();
    
    // Le bandeau "Abonnement manquant" ou un lien vers les abonnements devrait être visible
    // car on renvoie `null` pour `/subscriptions/me`
    await expect(page.locator('text=Mettre à niveau').or(page.locator('text=Abonnement')).first()).toBeVisible();
  });
});
