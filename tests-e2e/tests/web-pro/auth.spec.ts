import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('Web Pro - Authentification', () => {
  let mockBackend: MockBackend;

  test.beforeEach(async ({ page }) => {
    mockBackend = new MockBackend(page);
    await mockBackend.setup();
  });

  test('Doit pouvoir se connecter et compléter son profil (Onboarding)', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    
    // Étape 1 : Saisie du numéro
    await page.fill('input[type="tel"]', '771234567');
    await page.click('button:has-text("Continuer")');
    
    // Le composant d'OTP devrait s'afficher
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    
    // Étape 2 : OTP
    await page.fill('input[type="text"]', '123456');
    await page.click('button:has-text("Vérifier")');
    
    // Étape 3 : Onboarding Profil
    await expect(page.locator('text=Créer mon profil')).toBeVisible();
    
    // Remplir les informations
    await page.locator('input[type="text"]').nth(0).fill('Babacar Diop');
    await page.locator('input[placeholder="Ex: Dakar"]').fill('Dakar');
    
    // Sélection sport
    await page.click('text=Football');
    await page.click('button:has-text("Créer mon profil")');
    
    // Navigation dans le carousel
    await expect(page.locator('h2:has-text("Protégez vos photos")').last()).toBeVisible();
    await page.click('button:has-text("Suivant")');
    await page.click('button:has-text("Continuer")');

    // Page d'abonnement
    await expect(page.locator('text=Passez à la vitesse supérieure')).toBeVisible();
    await page.click('button:has-text("Plus tard, aller au tableau de bord")');
    
    // Redirection vers dashboard
    await expect(page.locator("text=Vue d'ensemble")).toBeVisible();
  });
});
