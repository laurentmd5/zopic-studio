import { test, expect } from '@playwright/test';
import { MockBackend } from '../utils/mock-api';

test.describe('PWA - Identité Sportive', () => {
  
  test.beforeEach(async ({ page }) => {
    const mockBackend = new MockBackend(page);
    await mockBackend.setup();
    
    // Mock the specific Identity endpoints
    await page.route('**/api/v1/athletes/slug-suggestions?base_slug=moussa', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ suggestions: ['moussa2', 'moussa.dkr', 'moussa_sport'] })
      });
    });

    await page.route('**/api/v1/athletes/me/profile', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            slug: 'moussa.dkr',
            is_public: 'PUBLIC',
            theme_color: 'blue'
          })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            slug: 'moussa.dkr',
            is_public: 'PUBLIC',
            bio: 'Lutteur professionnel',
            club: 'Fass',
            sport_attributes: { categorie: 'Lourds' },
            theme_color: 'red',
            is_verified: true,
            statistics: {
              competitions: 12,
              photos: 50,
              disciplines: 1,
              albums: 3,
              photographers: 2,
              active_since_year: 2026
            }
          })
        });
      }
    });

    await page.route('**/api/v1/public/athletes/moussa.dkr', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          slug: 'moussa.dkr',
          is_public: 'PUBLIC',
          bio: 'Lutteur professionnel',
          club: 'Fass',
          sport_attributes: { categorie: 'Lourds' },
          theme_color: 'red',
          is_verified: true,
          statistics: {
            competitions: 12,
            photos: 50,
            disciplines: 1,
            albums: 3,
            photographers: 2,
            active_since_year: 2026
          }
        })
      });
    });
  });

  test('Doit permettre de créer une identité avec un slug suggéré', async ({ page }) => {
    await page.goto('http://localhost:5174/identity/activate');
    
    // Étape 1 : Choix du slug
    await page.fill('input[name="slug"]', 'moussa');
    await page.click('button[type="submit"]');
    
    // Étape 2 : Sélection de la suggestion
    await expect(page.locator('text=@moussa.dkr')).toBeVisible();
    await page.click('text=@moussa.dkr');
    
    await page.click('button:has-text("Créer mon identité")');
    
    // Étape 3 : Transition
    await expect(page.locator('text=Import automatique...')).toBeVisible();
    
    // Redirection automatique vers /@moussa.dkr
    await page.waitForURL('**/@moussa.dkr');
    await expect(page.locator('text=@moussa.dkr')).toBeVisible();
  });

  test('Doit afficher les statistiques pré-calculées et le profil public', async ({ page }) => {
    await page.goto('http://localhost:5174/@moussa.dkr');
    
    await expect(page.locator('h1')).toContainText('@moussa.dkr');
    await expect(page.locator('text=Lutteur professionnel')).toBeVisible();
    await expect(page.locator('text=Fass')).toBeVisible();
    await expect(page.locator('text=categorie: Lourds')).toBeVisible();
    
    // Statistiques
    await expect(page.locator('text=12').first()).toBeVisible(); // Événements
    await expect(page.locator('text=50').first()).toBeVisible(); // Photos
  });
});
