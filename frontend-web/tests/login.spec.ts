import { test, expect } from '@playwright/test';

test('Photographer login and onboarding flow', async ({ page }) => {
  // Go to the login page
  await page.goto('/login');

  // Step 1: Phone number
  await expect(page.getByRole('heading', { name: 'Connexion / Inscription' })).toBeVisible();
  await page.getByPlaceholder('+221 77 123 45 67').fill('771234567');
  await page.getByRole('button', { name: 'Continuer' }).click();

  // Step 2: OTP
  await expect(page.getByRole('heading', { name: 'Vérification' })).toBeVisible();
  await page.getByPlaceholder('------').fill('123456');
  await page.getByRole('button', { name: 'Vérifier' }).click();

  // Step 3: Profile setup
  await expect(page.getByRole('heading', { name: 'Complétez votre profil' })).toBeVisible();
  // The first required input is "Nom Complet ou Nom du Studio *"
  // Since they don't have distinct ids, we can select by label or place in DOM.
  // Playwright can locate inputs by their adjacent label.
  await page.locator('input[type="text"]').first().fill('Studio Alpha');
  await page.locator('input[placeholder="Ex: Dakar"]').fill('Dakar');
  
  // Select a sport
  await page.getByText('Football', { exact: true }).click();
  await page.getByRole('button', { name: 'Créer mon profil' }).click();

  // Step 4: Carousel
  await expect(page.getByRole('heading', { name: 'Protégez vos photos' })).toBeVisible();
  await page.getByRole('button', { name: 'Suivant' }).click();
  await expect(page.getByRole('heading', { name: 'Gérez vos compétitions' })).toBeVisible();
  await page.getByRole('button', { name: 'Continuer' }).click();

  // Step 5: Subscription
  await expect(page.getByRole('heading', { name: 'Passez à la vitesse supérieure' })).toBeVisible();
  await page.getByRole('button', { name: 'Plus tard, aller au tableau de bord' }).click();

  // Step 6: Verify redirection to dashboard
  await expect(page).toHaveURL('/');
  // Checking that the dashboard layout is visible by looking for a generic dashboard element
  // Based on the router, '/' renders DashboardLayout and Dashboard
  // We can just verify the URL for now
});
