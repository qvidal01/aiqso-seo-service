/**
 * API Client for AIQSO SEO Service
 */

import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';

class APIClient {
  private client: AxiosInstance;
  private apiKey: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth header to all requests
    this.client.interceptors.request.use((config) => {
      if (this.apiKey) {
        config.headers['X-API-Key'] = this.apiKey;
      }
      return config;
    });
  }

  setApiKey(key: string) {
    this.apiKey = key;
    if (typeof window !== 'undefined') {
      localStorage.setItem('seo_api_key', key);
    }
  }

  getApiKey(): string | null {
    if (!this.apiKey && typeof window !== 'undefined') {
      this.apiKey = localStorage.getItem('seo_api_key');
    }
    return this.apiKey;
  }

  clearApiKey() {
    this.apiKey = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('seo_api_key');
    }
  }

  // Portal endpoints
  async getDashboard() {
    const { data } = await this.client.get('/portal/dashboard');
    return data;
  }

  async getWebsites() {
    const { data } = await this.client.get('/portal/websites');
    return data;
  }

  async getWebsiteAudits(websiteId: number, limit = 20) {
    const { data } = await this.client.get(`/portal/websites/${websiteId}/audits`, {
      params: { limit },
    });
    return data;
  }

  async getScoreHistory(websiteId: number, days = 30) {
    const { data } = await this.client.get(`/portal/websites/${websiteId}/score-history`, {
      params: { days },
    });
    return data;
  }

  async getWebsiteIssues(websiteId: number, status?: string) {
    const { data } = await this.client.get(`/portal/websites/${websiteId}/issues`, {
      params: { status },
    });
    return data;
  }

  async getAuditDetails(auditId: number) {
    const { data } = await this.client.get(`/portal/audits/${auditId}`);
    return data;
  }

  async requestAudit(websiteId: number, url?: string) {
    const { data } = await this.client.post('/portal/audits/request', null, {
      params: { website_id: websiteId, url },
    });
    return data;
  }

  async getAccount() {
    const { data } = await this.client.get('/portal/account');
    return data;
  }

  // Billing endpoints
  async getPlans() {
    const { data } = await this.client.get('/billing/plans');
    return data;
  }

  async getSubscription() {
    const { data } = await this.client.get('/billing/subscription');
    return data;
  }

  async getUsage() {
    const { data } = await this.client.get('/billing/usage');
    return data;
  }

  async createCheckout(tier: string, interval = 'monthly') {
    const { data } = await this.client.post('/billing/checkout', {
      tier,
      interval,
    });
    return data;
  }

  async getBillingPortal() {
    const { data } = await this.client.post('/billing/portal');
    return data;
  }

  async getPayments(limit = 20) {
    const { data } = await this.client.get('/billing/payments', {
      params: { limit },
    });
    return data;
  }

  // Work log endpoints
  async getWorkLogs(params?: { status?: string; category?: string; limit?: number }) {
    const { data } = await this.client.get('/worklog/entries', { params });
    return data;
  }

  async getWorkSummary(days = 30) {
    const { data } = await this.client.get('/worklog/summary', {
      params: { days },
    });
    return data;
  }

  async getProjects(status?: string) {
    const { data } = await this.client.get('/worklog/projects', {
      params: { status },
    });
    return data;
  }

  async getIssues(params?: { status?: string; website_id?: number; severity?: string }) {
    const { data } = await this.client.get('/worklog/issues', { params });
    return data;
  }

  // Audit endpoints
  async getAudits(limit = 50) {
    const { data } = await this.client.get('/portal/audits', {
      params: { limit },
    });
    return data;
  }

  async runAudit(url: string) {
    const { data } = await this.client.post('/audit', { url });
    return data;
  }

  // Work log convenience methods
  async getWorklog() {
    const entries = await this.getWorkLogs({ limit: 50 });
    return { entries };
  }

  async getWorklogSummary() {
    return this.getWorkSummary(30);
  }
}

export const api = new APIClient();
export default api;
