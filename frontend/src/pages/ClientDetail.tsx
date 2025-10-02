import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeftIcon,
  PencilIcon,
  LinkIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  CalendarIcon,
  ChartBarIcon,
  ClockIcon,
  EyeIcon,
  ShareIcon,
  BanknotesIcon,
  ChartPieIcon,
  BuildingOfficeIcon,
  PhoneIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';

interface Client {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status: string;
  onboarding_stage: string;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

interface PortalSubmission {
  id: number;
  client_id: number;
  project_requirements: string;
  budget_range: string;
  timeline: string;
  additional_info?: string;
  preferred_contact_method: string;
  urgency_level: string;
  status: string;
  created_at: string;
}

interface ClientStats {
  total_invoices: number;
  total_revenue: number;
  pending_invoices: number;
  total_tasks: number;
  completed_tasks: number;
  active_projects: number;
  monthly_recurring_revenue: number;
  lifetime_value: number;
  avg_project_value: number;
  payment_score: number;
}

interface Project {
  id: number;
  name: string;
  status: 'planning' | 'in_progress' | 'review' | 'completed' | 'on_hold';
  budget: number;
  spent: number;
  progress: number;
  start_date: string;
  deadline: string;
  manager: string;
}

interface Task {
  id: number;
  title: string;
  status: 'todo' | 'in_progress' | 'review' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee: string;
  due_date: string;
  project_id?: number;
}

interface Invoice {
  id: number;
  invoice_number: string;
  amount: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  issue_date: string;
  due_date: string;
  description: string;
}

const ClientDetail: React.FC = () => {
  const { id: clientId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch client details
  const { data: client, isLoading } = useQuery<Client>({
    queryKey: ['client', clientId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/clients/${clientId}`);
      return response.data;
    },
    enabled: !!clientId,
  });

  // Fetch portal submissions
  const { data: portalSubmissions } = useQuery<PortalSubmission[]>({
    queryKey: ['client-portal-submissions', clientId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/clients/${clientId}/portal-submissions`);
      return response.data;
    },
    enabled: !!clientId,
  });

  // Mock client stats - we'll implement the real API later
  const clientStats: ClientStats = {
    total_invoices: 12,
    total_revenue: 45000,
    pending_invoices: 2,
    total_tasks: 28,
    completed_tasks: 24,
    active_projects: 3,
    monthly_recurring_revenue: 5000,
    lifetime_value: 120000,
    avg_project_value: 8500,
    payment_score: 95,
  };

  // Mock projects data
  const projects: Project[] = [
    {
      id: 1,
      name: "Website Redesign",
      status: "in_progress",
      budget: 15000,
      spent: 8500,
      progress: 65,
      start_date: "2024-01-15",
      deadline: "2024-03-15",
      manager: "Sarah Johnson"
    },
    {
      id: 2,
      name: "SEO Campaign",
      status: "planning",
      budget: 8000,
      spent: 1200,
      progress: 15,
      start_date: "2024-02-01",
      deadline: "2024-05-01",
      manager: "Mike Chen"
    },
    {
      id: 3,
      name: "Social Media Strategy",
      status: "completed",
      budget: 5000,
      spent: 4800,
      progress: 100,
      start_date: "2023-11-01",
      deadline: "2024-01-01",
      manager: "Emily Davis"
    }
  ];

  // Mock tasks data
  const tasks: Task[] = [
    {
      id: 1,
      title: "Design homepage mockup",
      status: "completed",
      priority: "high",
      assignee: "Sarah Johnson",
      due_date: "2024-02-20",
      project_id: 1
    },
    {
      id: 2,
      title: "Content strategy review",
      status: "in_progress",
      priority: "medium",
      assignee: "Mike Chen",
      due_date: "2024-02-25",
      project_id: 2
    },
    {
      id: 3,
      title: "Client feedback incorporation",
      status: "todo",
      priority: "urgent",
      assignee: "Emily Davis",
      due_date: "2024-02-22",
      project_id: 1
    }
  ];

  // Mock invoices data
  const invoices: Invoice[] = [
    {
      id: 1,
      invoice_number: "INV-2024-001",
      amount: 7500,
      status: "paid",
      issue_date: "2024-01-15",
      due_date: "2024-02-15",
      description: "Website redesign - Phase 1"
    },
    {
      id: 2,
      invoice_number: "INV-2024-002",
      amount: 3200,
      status: "sent",
      issue_date: "2024-02-01",
      due_date: "2024-03-01",
      description: "SEO setup and initial optimization"
    },
    {
      id: 3,
      invoice_number: "INV-2024-003",
      amount: 2800,
      status: "overdue",
      issue_date: "2024-01-01",
      due_date: "2024-02-01",
      description: "Social media content creation"
    }
  ];

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      inactive: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.inactive;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const copyClientPortalLink = () => {
    const portalLink = `${window.location.origin}/client-portal/${client?.id}`;
    navigator.clipboard.writeText(portalLink);
    alert('Client portal link copied to clipboard!');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!client) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Client not found</h2>
        <Button onClick={() => navigate('/clients')} className="mt-4">
          Back to Clients
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => navigate('/clients')}
            className="flex items-center gap-2"
          >
            <ArrowLeftIcon className="h-4 w-4" />
            Back to Clients
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{client.name}</h1>
            <div className="flex items-center gap-3 mt-2">
              <Badge className={getStatusColor(client.status)}>
                {client.status}
              </Badge>
              <span className="text-gray-600">•</span>
              <span className="text-gray-600">{client.onboarding_stage}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={copyClientPortalLink}
            className="flex items-center gap-2"
          >
            <LinkIcon className="h-4 w-4" />
            Copy Portal Link
          </Button>
          <Button
            className="flex items-center gap-2"
          >
            <PencilIcon className="h-4 w-4" />
            Edit Client
          </Button>
        </div>
      </div>

      {/* Enhanced Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(clientStats.total_revenue)}
                </p>
              </div>
              <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">MRR</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(clientStats.monthly_recurring_revenue)}
                </p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">LTV</p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatCurrency(clientStats.lifetime_value)}
                </p>
              </div>
              <ChartPieIcon className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Projects</p>
                <p className="text-2xl font-bold text-orange-600">{clientStats.active_projects}</p>
              </div>
              <BuildingOfficeIcon className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Payment Score</p>
                <p className="text-2xl font-bold text-green-600">{clientStats.payment_score}%</p>
              </div>
              <BanknotesIcon className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Project</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {formatCurrency(clientStats.avg_project_value)}
                </p>
              </div>
              <DocumentTextIcon className="h-8 w-8 text-indigo-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Client Information Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-semibold">Contact Information</CardTitle>
            <EnvelopeIcon className="h-5 w-5 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                <span className="text-sm">{client.email}</span>
              </div>
              {client.phone && (
                <div className="flex items-center gap-3">
                  <PhoneIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm">{client.phone}</span>
                </div>
              )}
              {client.company && (
                <div className="flex items-center gap-3">
                  <BuildingOfficeIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm">{client.company}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
            <ShareIcon className="h-5 w-5 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <DocumentTextIcon className="h-4 w-4 mr-2" />
                Create Invoice
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <CheckCircleIcon className="h-4 w-4 mr-2" />
                Add Task
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <CalendarIcon className="h-4 w-4 mr-2" />
                Schedule Meeting
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
            <ClockIcon className="h-5 w-5 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="h-2 w-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium">Invoice paid</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium">Task completed</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="h-2 w-2 bg-yellow-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium">Status updated</p>
                  <p className="text-xs text-gray-500">3 days ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comprehensive Dashboard Tabs */}
      <div className="mt-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: ChartBarIcon },
              { id: 'projects', label: 'Projects', icon: DocumentTextIcon },
              { id: 'tasks', label: 'Tasks', icon: CheckCircleIcon },
              { id: 'finance', label: 'Finance', icon: CurrencyDollarIcon },
              { id: 'portal', label: 'Portal Submissions', icon: DocumentTextIcon },
              { id: 'analytics', label: 'Analytics', icon: ChartPieIcon },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Project Health</CardTitle>
                  <CardDescription>Current project status overview</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {projects.map((project) => (
                      <div key={project.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{project.name}</h4>
                          <Badge className={project.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                          project.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 
                                          'bg-yellow-100 text-yellow-800'}>
                            {project.status.replace('_', ' ')}
                          </Badge>
                        </div>
                        <div className="mb-2">
                          <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Progress</span>
                            <span>{project.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all" 
                              style={{ width: `${project.progress}%` }}
                            ></div>
                          </div>
                        </div>
                        <div className="flex justify-between text-sm text-gray-600">
                          <span>Budget: {formatCurrency(project.spent)} / {formatCurrency(project.budget)}</span>
                          <span>Due: {new Date(project.deadline).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Task Summary</CardTitle>
                  <CardDescription>Recent and upcoming tasks</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {tasks.map((task) => (
                      <div key={task.id} className="flex items-center gap-3 p-3 border rounded-lg">
                        <div className={`h-3 w-3 rounded-full ${
                          task.status === 'completed' ? 'bg-green-500' :
                          task.status === 'in_progress' ? 'bg-blue-500' :
                          'bg-gray-300'
                        }`}></div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{task.title}</p>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span>Assigned to: {task.assignee}</span>
                            <span>•</span>
                            <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <Badge className={task.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                                        task.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                                        'bg-green-100 text-green-800'}>
                          {task.priority}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Projects</h2>
                <Button>
                  <DocumentTextIcon className="h-4 w-4 mr-2" />
                  New Project
                </Button>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <Card key={project.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{project.name}</CardTitle>
                        <Badge className={project.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                        project.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 
                                        'bg-yellow-100 text-yellow-800'}>
                          {project.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Progress</span>
                            <span>{project.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all" 
                              style={{ width: `${project.progress}%` }}
                            ></div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Budget</p>
                            <p className="font-medium">{formatCurrency(project.budget)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Spent</p>
                            <p className="font-medium">{formatCurrency(project.spent)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Start Date</p>
                            <p className="font-medium">{new Date(project.start_date).toLocaleDateString()}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Deadline</p>
                            <p className="font-medium">{new Date(project.deadline).toLocaleDateString()}</p>
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-gray-600 text-sm">Project Manager</p>
                          <p className="font-medium">{project.manager}</p>
                        </div>
                        
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <EyeIcon className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button size="sm" variant="outline">
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Tasks</h2>
                <Button>
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  New Task
                </Button>
              </div>
              <Card>
                <CardContent className="p-0">
                  <div className="divide-y">
                    {tasks.map((task) => (
                      <div key={task.id} className="p-4 hover:bg-gray-50">
                        <div className="flex items-center gap-4">
                          <div className={`h-4 w-4 rounded-full ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'in_progress' ? 'bg-blue-500' :
                            'bg-gray-300'
                          }`}></div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium">{task.title}</h4>
                              <div className="flex items-center gap-2">
                                <Badge className={task.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                                                task.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                                                'bg-green-100 text-green-800'}>
                                  {task.priority}
                                </Badge>
                                <Badge className="border border-gray-300 bg-white text-gray-700">
                                  {task.status.replace('_', ' ')}
                                </Badge>
                              </div>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                              <span>Assigned to: {task.assignee}</span>
                              <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                              {task.project_id && (
                                <span>Project: {projects.find(p => p.id === task.project_id)?.name}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <EyeIcon className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <PencilIcon className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'finance' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Finance</h2>
                <Button>
                  <CurrencyDollarIcon className="h-4 w-4 mr-2" />
                  New Invoice
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Total Revenue</p>
                      <p className="text-2xl font-bold text-green-600">{formatCurrency(clientStats.total_revenue)}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Outstanding</p>
                      <p className="text-2xl font-bold text-red-600">{formatCurrency(8000)}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">This Month</p>
                      <p className="text-2xl font-bold text-blue-600">{formatCurrency(clientStats.monthly_recurring_revenue)}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Payment Score</p>
                      <p className="text-2xl font-bold text-green-600">{clientStats.payment_score}%</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Invoices</CardTitle>
                  <CardDescription>Recent invoices and payment history</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {invoices.map((invoice) => (
                      <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h4 className="font-medium">{invoice.invoice_number}</h4>
                          <p className="text-sm text-gray-600">{invoice.description}</p>
                          <p className="text-xs text-gray-500">
                            Issued: {new Date(invoice.issue_date).toLocaleDateString()} • 
                            Due: {new Date(invoice.due_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{formatCurrency(invoice.amount)}</p>
                          <Badge className={invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                                          invoice.status === 'overdue' ? 'bg-red-100 text-red-800' :
                                          'bg-yellow-100 text-yellow-800'}>
                            {invoice.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Analytics & Reports</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Revenue Trends</CardTitle>
                    <CardDescription>Monthly revenue over time</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      <div className="text-center">
                        <ChartBarIcon className="h-12 w-12 mx-auto mb-2" />
                        <p>Revenue chart coming soon</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Project Performance</CardTitle>
                    <CardDescription>Budget vs actual spending</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      <div className="text-center">
                        <ChartPieIcon className="h-12 w-12 mx-auto mb-2" />
                        <p>Performance chart coming soon</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'portal' && (
            <Card>
              <CardHeader>
                <CardTitle>Portal Submissions</CardTitle>
                <CardDescription>Client project requirements submitted through the portal</CardDescription>
              </CardHeader>
              <CardContent>
                {portalSubmissions && portalSubmissions.length > 0 ? (
                  <div className="space-y-4">
                    {portalSubmissions.map((submission) => (
                      <div key={submission.id} className="border border-gray-200 rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              Submission #{submission.id}
                            </h4>
                            <p className="text-sm text-gray-500">
                              Submitted on {new Date(submission.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge className={submission.status === 'new' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}>
                            {submission.status}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <h5 className="font-medium text-gray-900 mb-2">Project Requirements</h5>
                            <p className="text-gray-700 text-sm mb-4">{submission.project_requirements}</p>
                            
                            <h5 className="font-medium text-gray-900 mb-2">Budget Range</h5>
                            <p className="text-gray-700 text-sm mb-4">{submission.budget_range}</p>
                            
                            <h5 className="font-medium text-gray-900 mb-2">Timeline</h5>
                            <p className="text-gray-700 text-sm">{submission.timeline}</p>
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-gray-900 mb-2">Priority Level</h5>
                            <Badge 
                              className={submission.urgency_level === 'urgent' ? 'bg-red-100 text-red-800' : 
                                       submission.urgency_level === 'high' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}
                            >
                              {submission.urgency_level}
                            </Badge>
                            
                            <h5 className="font-medium text-gray-900 mb-2 mt-4">Preferred Contact</h5>
                            <p className="text-gray-700 text-sm mb-4">{submission.preferred_contact_method}</p>
                            
                            {submission.additional_info && (
                              <>
                                <h5 className="font-medium text-gray-900 mb-2">Additional Information</h5>
                                <p className="text-gray-700 text-sm">{submission.additional_info}</p>
                              </>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
                          <Button size="sm" variant="outline">
                            Mark as Reviewed
                          </Button>
                          <Button size="sm" variant="outline">
                            Send Proposal
                          </Button>
                          <Button size="sm" variant="outline">
                            Schedule Call
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Portal Submissions</h3>
                    <p className="text-gray-600 mb-4">This client hasn't submitted any project requirements through the portal yet.</p>
                    <Button 
                      variant="outline"
                      onClick={copyClientPortalLink}
                      className="flex items-center gap-2 mx-auto"
                    >
                      <LinkIcon className="h-4 w-4" />
                      Share Portal Link
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ClientDetail;
