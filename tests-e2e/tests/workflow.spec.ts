import { test, expect } from '@playwright/test';

test.describe('ZoPic Studio - Workflow E2E complet', () => {

  test('Photographe crée une compétition et client l\'achète', async ({ context, browser }) => {
    // ==========================================
    // 1. MOCK API - Backend Simulation
    // ==========================================
    
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': '*'
    };

    let mockCompetitions = [];

    // Single route handler for all backend API calls
    await context.route('http://localhost:8000/api/v1/**', async (route, request) => {
      const url = request.url();
      const method = request.method();
      console.log(`[MOCK] Intercepted: ${method} ${url}`);

      if (method === 'OPTIONS') {
        await route.fulfill({ status: 200, headers: corsHeaders });
        return;
      }

      if (url.includes('/api/v1/competitions/999') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify({
            id: 999,
            name: 'Marathon de Dakar E2E',
            status: 'Publié',
            date: new Date().toISOString(),
            settings: { price_per_photo: 1500 },
            photos_count: 3
          })
        });
        return;
      }

      if (url.includes('/api/v1/search/competitions/999') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify({
            results: [
              { id: 1, url: 'mock-image-1.jpg', price: 1500, watermark_url: 'mock-image-1.jpg' },
              { id: 2, url: 'mock-image-2.jpg', price: 1500, watermark_url: 'mock-image-2.jpg' }
            ]
          })
        });
        return;
      }

      if (url.includes('/api/v1/competitions') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(mockCompetitions)
        });
        return;
      }

      if (url.includes('/api/v1/competitions') && method === 'POST') {
        const payload = request.postDataJSON();
        const newComp = {
          id: 999,
          name: payload.name,
          date: payload.date,
          status: 'Brouillon',
          photos_count: 0
        };
        mockCompetitions.push(newComp);
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(newComp)
        });
        return;
      }

      if (url.includes('/api/v1/payments/init') && method === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify({
            payment_url: 'http://localhost:5174/downloads?success=true',
            transaction_id: 'txn_mock_123'
          })
        });
        return;
      }

      // Default fallback if we missed something
      await route.continue();
    });

    // ==========================================
    // 2. DASHBOARD PRO (Photographe)
    // ==========================================
    const pagePro = await context.newPage();
    await pagePro.goto('http://localhost:5173/login');
    
    // Login Flow
    await pagePro.fill('input[type="tel"]', '771234567');
    await pagePro.click('button[type="submit"]'); // Continuer
    
    await pagePro.fill('input[type="text"]', '123456'); // OTP
    await pagePro.click('button[type="submit"]'); // Vérifier
    
    // Formulaire de profil
    await pagePro.locator('input[type="text"]').first().fill('Test Studio'); // fullName
    await pagePro.fill('input[placeholder="Ex: Dakar"]', 'Dakar');
    await pagePro.click('text=Football'); // Choisir un sport
    await pagePro.click('button[type="submit"]'); // Créer mon profil
    
    // Carousel
    await pagePro.click('button:has-text("Suivant")');
    await pagePro.click('button:has-text("Continuer")');
    
    // Subscription
    await pagePro.click('button:has-text("Plus tard, aller au tableau de bord")');
    
    // Attendre le Dashboard
    await expect(pagePro.locator('text=Vue d\'ensemble')).toBeVisible();

    // Aller sur Competitions et créer
    await pagePro.goto('http://localhost:5173/competitions');
    await pagePro.click('text=Nouvelle compétition');
    
    // Remplir formulaire
    await pagePro.fill('input[placeholder="Ex: Marathon de Dakar"]', 'Marathon de Dakar E2E');
    await pagePro.fill('input[type="date"]', '2026-10-10');
    await pagePro.fill('input[placeholder="Ex: Corniche Ouest, Dakar"]', 'Dakar');
    await pagePro.locator('form select').selectOption('Running');
    await pagePro.fill('input[placeholder="Ex: 10km, Semi-Marathon, Élite"]', '10km');
    await pagePro.fill('input[type="number"]', '1500');
    
    // Soumettre
    await pagePro.click('button:has-text("Créer")');
    await expect(pagePro.locator('h3:has-text("Marathon de Dakar E2E")')).toBeVisible();
    
    // Aller sur le détail
    await pagePro.locator('h3:has-text("Marathon de Dakar E2E")').click();
    await expect(pagePro.locator('text=Marathon de Dakar E2E').first()).toBeVisible();
    
    // ==========================================
    // 3. PWA CLIENT (Athlète)
    // ==========================================
    const pageClient = await context.newPage();
    await pageClient.goto('http://localhost:5174/competition/999');
    
    // Vérifie qu'on est sur la page
    await expect(pageClient.locator('h1', { hasText: 'Marathon de Dakar E2E' })).toBeVisible();
    
    await pageClient.click('button:has-text("Retrouver mes photos")');
    
    // Clique sur la recherche "Tout" (qui simule la recherche globale)
    await pageClient.click('text=Tout');

    // Vérifie que les photos s'affichent
    await expect(pageClient.locator('text=Résultats')).toBeVisible({ timeout: 10000 });
    
    // Ajoute au panier (cliquer sur la première photo)
    await pageClient.locator('.photo-card').first().click();
    
    // Ouvre le panier en bas de l'écran
    await pageClient.click('button:has-text("Panier")');
    await expect(pageClient.locator('text=1500 FCFA').first()).toBeVisible();
    
    // Remplir le checkout (seulement le téléphone)
    await pageClient.fill('input[type="tel"]', '771234567');
    await pageClient.click('button:has-text("Payer 1500 FCFA")');

    // On s'attend à être redirigé vers la page de succès/téléchargements
    // Car le mock de paiement redirige vers /downloads?success=true
    await expect(pageClient).toHaveURL(/.*downloads.*/);
  });

});
