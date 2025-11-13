# Integration Test Validation Strategy

## The Problem

Integration tests must validate that the UI actually works correctly, not just that it renders something. Weak assertions like `expect(pageContent).toBeTruthy()` don't prove the application is functioning.

## The Solution: Three-Layer Validation

For each integration test, validate at three layers:

### 1. API Layer - Verify Backend State
After any action (user interaction or API call), query the backend API to verify:
- Data was saved correctly
- State changes were persisted
- Values match what was submitted

**Example:**
```typescript
// Submit data
await request.post("/api/v0/result", { data: { value: 123 } });

// Verify backend actually stored it
const response = await request.get("/api/v0/result/test-name");
expect(response.status()).toBe(200);
const data = await response.json();
expect(data.results[0].value).toBe(123); // Verify actual value
```

### 2. UI Layer - Verify Visual Representation
Check that the UI displays the correct data:
- Specific text/values appear on screen
- UI elements are in the correct state
- Data from backend is rendered properly

**Example:**
```typescript
// Verify UI shows the actual data
await expect(page.locator('text=123')).toBeVisible();
// Not just: expect(pageContent).toBeTruthy() ❌
```

### 3. Cross-Validation - API ↔ UI Consistency
Verify the UI displays exactly what the API returns:

**Example:**
```typescript
// Get data from API
const apiResponse = await request.get("/api/v0/result/test-name");
const apiData = await apiResponse.json();

// Navigate to UI
await page.goto("/result/test-name");

// Verify UI shows API data
await expect(page.locator(`text=${apiData.value}`)).toBeVisible();
await expect(page.locator(`text=${apiData.unit}`)).toBeVisible();
```

## Anti-Patterns to Avoid

### ❌ Weak Assertions
```typescript
const pageContent = await page.content();
expect(pageContent).toBeTruthy(); // Too weak!
```

### ❌ No Backend Verification
```typescript
// Submit via API
await request.post("/api/v0/result", { data });

// Navigate to UI
await page.goto("/dashboard");

// Only check UI loaded, don't verify data ❌
await expect(page.locator("#main-content")).toBeVisible();
```

### ❌ Status Code Only
```typescript
const response = await request.post("/api/v0/result", { data });
expect(response.status()).toBe(200); // Not enough!
// Should also verify response body and query backend
```

## Best Practices

### ✅ Complete Validation Chain
```typescript
test("should create and display test result", async ({ page, request }) => {
  const token = await page.evaluate(() => localStorage.getItem("token"));
  const testName = "integration-test-" + Date.now();

  // 1. Submit data via API
  const submitResponse = await request.post("/api/v0/result", {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      test_name: testName,
      value: 456.78,
      unit: "ms",
    },
  });

  // 2. Verify API accepted it
  expect(submitResponse.status()).toBe(200);
  const submitData = await submitResponse.json();
  expect(submitData).toHaveProperty("result_id");

  // 3. Verify backend stored it correctly
  const verifyResponse = await request.get(`/api/v0/result/${testName}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(verifyResponse.status()).toBe(200);
  const storedData = await verifyResponse.json();
  expect(storedData.results).toBeDefined();
  expect(storedData.results[0].value).toBe(456.78);
  expect(storedData.results[0].unit).toBe("ms");

  // 4. Navigate to UI
  await page.goto("/tests");
  await page.waitForTimeout(2000);

  // 5. Verify UI displays the backend data
  await expect(page.locator(`text=${testName}`)).toBeVisible();
  await expect(page.locator('text=456.78')).toBeVisible();

  // 6. Cross-validate: click through to detail page
  await page.click(`text=${testName}`);
  await page.waitForURL(`/result/${testName}`);

  // 7. Verify detail page shows correct data
  await expect(page.locator(`text=${testName}`)).toBeVisible();
  await expect(page.locator('text=456.78')).toBeVisible();
  await expect(page.locator('text=ms')).toBeVisible();
});
```

### ✅ Validate State Changes
```typescript
test("should update test to public", async ({ page, request }) => {
  const token = await page.evaluate(() => localStorage.getItem("token"));
  const testName = "test-" + Date.now();

  // Create test
  await request.post("/api/v0/result", { ... });

  // Make it public
  await request.post(`/api/v0/config/${testName}`, {
    data: [{ public: true }],
  });

  // Verify backend config changed
  const configResponse = await request.get(`/api/v0/config/${testName}`);
  const config = await configResponse.json();
  expect(config[0].public).toBe(true); // ✅ Verify actual state

  // Verify it appears in public list
  const publicResponse = await request.get("/api/v0/public");
  const publicData = await publicResponse.json();
  const ourTest = publicData.find(t => t.test_name === testName);
  expect(ourTest).toBeDefined(); // ✅ Verify it's actually there
  expect(ourTest.test_name).toBe(testName); // ✅ Verify correct data
});
```

## Testing Checklist

For each integration test, ask:

- [ ] Does the test verify the API accepted the data? (status + response body)
- [ ] Does the test query the backend to confirm data persistence?
- [ ] Does the test verify the actual values, not just presence of data?
- [ ] Does the test check the UI displays specific, correct data?
- [ ] Does the test validate UI state matches backend state?
- [ ] Would this test catch if we displayed wrong data?
- [ ] Would this test catch if data wasn't actually saved?

## Examples of Improved Tests

### Before (Weak)
```typescript
test("should view test results", async ({ page }) => {
  await page.goto("/tests");
  const pageContent = await page.content();
  expect(pageContent).toBeTruthy(); // ❌ Too weak
});
```

### After (Strong)
```typescript
test("should view test results", async ({ page, request }) => {
  const token = await page.evaluate(() => localStorage.getItem("token"));

  // Create known test data
  const testName = "validation-test-" + Date.now();
  await request.post("/api/v0/result", {
    headers: { Authorization: `Bearer ${token}` },
    data: { test_name: testName, value: 123.45, unit: "ms" },
  });

  // Verify backend has it
  const apiData = await request.get(`/api/v0/result/${testName}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect((await apiData.json()).results[0].value).toBe(123.45);

  // Check UI displays it
  await page.goto("/tests");
  await expect(page.locator(`text=${testName}`)).toBeVisible(); // ✅ Specific
  await expect(page.locator('text=123.45')).toBeVisible(); // ✅ Actual value
});
```

## Conclusion

Integration tests must validate the complete flow: API → Database → UI. Each layer must be verified with specific assertions about actual data, not just presence checks.

**Remember:** If your test would pass even when displaying wrong data, it's not a good test!
