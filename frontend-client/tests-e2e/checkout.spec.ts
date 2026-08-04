import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test('User can search and complete checkout', async ({ page }) => {
    // Mock search API
    await page.route('**/api/v1/public/athletes/search*', async route => {
      await route.fulfill({ json: [{ id: 1, name: 'Event', date: '2023' }] });
    });

    // 1. Visit Home
    await page.goto('/');
    await expect(page).toHaveTitle(/ZoPic/i);

    // 2. Click Search (Rechercher mes photos)
    await page.click('text="Trouver mes photos"', { force: true });
    await expect(page).toHaveURL(/.*\/search/);

    // 3. Search by Dossard
    await page.fill('input[placeholder="Numéro de dossard"]', '12345');
    await page.click('button:has-text("Rechercher")');

    // 4. In a real app we'd wait for results. Here we assume we navigate to /competition/1
    // Actually the mock in SearchPage navigates to /competition/1 after search
    await page.waitForURL(/.*\/competition\/1/);
    
    // 5. Select a photo and add to cart
    // Wait for photos to appear (mock data might take a bit or appear instantly)
    // We can just click the first "Ajouter au panier" button
    await page.waitForSelector('text="Ajouter au panier"');
    await page.click('text="Ajouter au panier"', { matchFallback: true });

    // 6. Go to checkout (Clicking on Panier in BottomNav or the CTA)
    await page.click('text="Voir le panier"', { force: true });
    await expect(page).toHaveURL(/.*\/checkout/);

    // 7. Verify Checkout Page
    await expect(page.locator('text="Votre Panier"')).toBeVisible();
    await page.click('text="Passer à la caisse"');

    // 8. Select Payment Method
    await expect(page).toHaveURL(/.*\/payment/);
    // Click on Wave (for example)
    await page.click('text="Wave"', { force: true });
    await page.click('text="Payer"', { force: true });

    // 9. Should redirect to Purchases
    await page.waitForURL(/.*\/purchases/);
    await expect(page.locator('text="Mes Achats"')).toBeVisible();
  });
});
