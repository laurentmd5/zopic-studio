import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test('User can search and complete checkout', async ({ page }) => {
    // Mock search API
    await page.route('**/api/v1/faces/search*', async route => {
      await route.fulfill({ json: { results: [{ photo_id: 1, url: 'mock.jpg', price_xof: 500 }] } });
    });

    // 1. Visit Home
    await page.goto('/');
    await expect(page).toHaveTitle(/ZoPic/i);

    // 2. Click Search (Rechercher mes photos)
    await page.click('text="Trouver mes photos"', { force: true });
    await expect(page).toHaveURL(/.*\/search/);

    // 3. Search by File Upload (since selfie search is the main flow)
    await page.check('input[type="checkbox"]');
    await page.setInputFiles('input[type="file"]', {
      name: 'selfie.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from('mock-image-data')
    });

    // 4. Wait for search to complete and results to be displayed
    await page.waitForSelector('text="Résultats"');
    
    // 5. Select a photo and add to cart
    await page.waitForSelector('.photo-item');
    await page.click('.photo-item'); // clicks the first photo item

    // 6. Go to checkout (Clicking on Panier in BottomNav or the CTA)
    await page.click('text="Voir le panier"', { force: true });
    await expect(page).toHaveURL(/.*\/checkout/);

    // 7. Verify Checkout Page
    await expect(page.locator('text="Panier"')).toBeVisible();
    await page.click('text="Procéder au paiement"');

    // 8. Select Payment Method
    await expect(page).toHaveURL(/.*\/payment/);
    // Click on Wave (for example)
    await page.click('text="Wave"', { force: true });
    await page.click('button:has-text("Payer")', { force: true });

    // 9. Should redirect to Purchases
    await page.waitForURL(/.*\/purchases/);
    await expect(page.locator('text="Mes achats"')).toBeVisible();
  });
});
