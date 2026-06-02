import { http, HttpResponse } from 'msw';
import mockBillingData from './mockBilling.json';

export const handlers = [
  http.get('/api/v0/user/config', () =>
    HttpResponse.json(mockBillingData.user_config[1])
  ),
  http.get('/api/v0/user/meters', () =>
    HttpResponse.json(mockBillingData.user_meters[0])
  ),
  http.get('/api/v0/orgs/subscriptions', () =>
    HttpResponse.json(mockBillingData.orgs_subscriptions[2].orgs)
  ),
];
