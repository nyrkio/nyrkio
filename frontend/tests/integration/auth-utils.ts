import { expect, type Page } from "@playwright/test";

const env = (globalThis as any).process?.env || {};

export const BACKEND_BASE_URL = env.BACKEND_BASE_URL || "http://localhost:8001";

export async function loginWithCookie(page: Page, email: string, password: string) {
  const response = await page.request.post(
    `${BACKEND_BASE_URL}/api/v0/auth/cookie/login`,
    {
      form: {
        username: email,
        password: password,
      },
    },
  );

  if (!response.ok()) {
    throw new Error(
      `Login failed with status ${response.status()}: ${await response.text()}`,
    );
  }

  await page.goto("/");

  await expect.poll(async () => {
    const auth = await page.request.get(
      `${BACKEND_BASE_URL}/api/v0/auth/authenticated-route`,
    );
    return auth.status();
  }).toBe(200);
}

export async function getJwtToken(page: Page, email: string, password: string) {
  const response = await page.request.post(
    `${BACKEND_BASE_URL}/api/v0/auth/jwt/login`,
    {
      form: {
        username: email,
        password: password,
      },
    },
  );

  if (!response.ok()) {
    throw new Error(
      `JWT login failed with status ${response.status()}: ${await response.text()}`,
    );
  }

  const body = await response.json();
  return body.access_token as string;
}
