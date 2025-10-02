export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface Client {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status: 'pending' | 'active' | 'completed' | 'inactive';
  onboarding_stage: string;
  created_at: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  client_id: number;
  amount: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  due_date: string;
  paid_date?: string;
  description?: string;
  created_at: string;
}

export interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  source?: string;
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface ContentPost {
  id: number;
  title: string;
  content?: string;
  platform: string;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_for?: string;
  published_at?: string;
  engagement_data?: any;
  ai_generated: boolean;
  created_at: string;
}

export interface AIScript {
  id: number;
  topic: string;
  script_content?: string;
  video_style: string;
  target_duration: number;
  status: 'draft' | 'generated' | 'video_created';
  metadata?: any;
  created_at: string;
}

export interface DashboardStats {
  total_clients: number;
  active_clients: number;
  pending_tasks: number;
  new_leads: number;
  revenue_this_month: number;
  content_posts_scheduled: number;
}
