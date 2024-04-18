import { test, expect } from 'playwright/test';

test('logo on front page', async ({ page }) => {
  await page.goto('./');
  var img = page.locator('img.nyrkio-logo-img-default');
  console.log(img);
  //await expect(img).toHaveAttribute('src', /NyrkioLogo_Final_Full_Brown-800px.png/);
  await expect(img).toHaveAttribute('alt', 'Nyrkiö (logo)');
});

