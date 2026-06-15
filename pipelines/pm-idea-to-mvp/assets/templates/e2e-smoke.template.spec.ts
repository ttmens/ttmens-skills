import { test, expect } from '@playwright/test';

/**
 * Smoke spec — replace paths with P0 screens from 03b-user-journey.md
 */
test.describe('P0 smoke', () => {
  test('home loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
    await expect(page.locator('body')).toBeVisible();
  });

  // test('core journey step', async ({ page }) => {
  //   await page.goto('/dashboard');
  //   await expect(page.getByRole('navigation')).toBeVisible();
  // });
});
