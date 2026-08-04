import { test, expect } from '@playwright/test';

test.describe('Athlete Flow', () => {
  test('User can edit identity and view timeline', async ({ page }) => {
    // Mock API requests
    await page.route('**/api/v1/athletes/me/profile*', async route => {
      const mockProfile = { slug: 'moussa', bio: 'Hello', club: '', nationality: '', theme_color: 'green', sport_attributes: {}, is_public: 'PUBLIC' };
      if (route.request().method() === 'PUT') {
        await route.fulfill({ json: { success: true } });
      } else {
        await route.fulfill({ json: mockProfile });
      }
    });

    // 1. Visit Edit Identity
    await page.goto('/identity/edit');
    await expect(page.locator('text="Mon Profil"')).toBeVisible();

    // 2. Edit fields
    await page.fill('input[name="club"]', 'FC Playwright');
    await page.fill('input[name="nationality"]', 'Dakar, Sénégal');
    await page.fill('textarea[name="bio"]', 'Automation testing is great');
    
    // Save
    await page.click('text="Enregistrer"', { force: true });
    
    // It should navigate to /@slug
    // Assuming mock slug is returned. For now we just verify the URL changes or a toast appears.
    // We can't guarantee what the slug is, so we just wait for URL to not be /identity/edit
    await page.waitForURL(url => !url.href.includes('/identity/edit'));

    // 3. Visit Timeline
    await page.goto('/timeline');
    await expect(page.locator('text="Ma Carrière"')).toBeVisible();
    // Wait for the timeline to load and show either empty state or some years
    // The text 'Votre carrière sportive' or 'Aucune compétition' should be visible
    const hasTimeline = await page.locator('text="Votre carrière sportive"').isVisible();
    const hasEmpty = await page.locator('text="Aucune compétition"').isVisible();
    expect(hasTimeline || hasEmpty).toBeTruthy();
  });
});
