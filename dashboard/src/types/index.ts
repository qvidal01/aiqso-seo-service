/**
 * Type definitions for AIQSO SEO Service Dashboard
 */

export interface Audit {
  id: number;
  domain: string;
  score: number;
  critical_count: number;
  warning_count: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
}

export interface Issue {
  id: number;
  title: string;
  description: string;
  severity: 'critical' | 'warning' | 'info';
  status: 'open' | 'in_progress' | 'resolved';
  domain: string;
  recommendation?: string;
  fix_price_cents?: number;
  created_at: string;
}

export interface Website {
  id: number;
  domain: string;
  status: 'healthy' | 'warning' | 'critical';
  last_audit_score: number | null;
  last_audit_at: string | null;
  issues_count: number;
  warnings_count: number;
}

export interface Payment {
  id: number;
  amount_cents: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed';
  description?: string;
  created_at: string;
}

export interface Subscription {
  id: number;
  tier_name: string;
  status: 'active' | 'canceled' | 'past_due';
  amount_cents: number;
  current_period_end: string;
}

export interface WorklogEntry {
  id: number;
  title: string;
  description?: string;
  category: 'audit' | 'fix' | 'optimization' | 'consultation' | 'monitoring';
  actual_minutes: number;
  hourly_rate_cents: number;
  project_name?: string;
  created_at: string;
}

export interface WorklogSummary {
  this_month_minutes: number;
  billable_amount_cents: number;
  completed_tasks: number;
  active_projects: number;
}

export interface DashboardData {
  avg_score: number | null;
  score_change?: number;
  total_websites: number;
  open_issues: number;
  audits_this_month: number;
  recent_audits?: Audit[];
  top_issues?: Issue[];
}

export type StatusFilter = 'all' | 'open' | 'in_progress' | 'resolved';
export type SeverityFilter = 'all' | 'critical' | 'warning' | 'info';
