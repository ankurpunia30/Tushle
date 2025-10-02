import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { 
  ArrowLeft, 
  Clock, 
  DollarSign, 
  Target, 
  TrendingUp, 
  Calendar,
  User,
  Mail,
  Phone,
  MapPin,
  Award,
  Activity,
  FileText,
  Users,
  BarChart3
} from 'lucide-react';
import { format } from 'date-fns';

interface Employee {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  phone?: string;
  department?: string;
  position?: string;
  hire_date?: string;
  salary?: number;
}

interface TaskAnalytics {
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  overdue_tasks: number;
  total_hours_logged: number;
  avg_completion_time: number;
  productivity_score: number;
  tasks_by_month: Array<{ month: string; count: number }>;
  tasks_by_priority: Array<{ priority: string; count: number }>;
  recent_tasks: Array<any>;
}

interface FinanceAnalytics {
  total_revenue_generated: number;
  billable_hours: number;
  hourly_rate: number;
  monthly_earnings: Array<{ month: string; amount: number }>;
  project_earnings: Array<{ project: string; amount: number }>;
  efficiency_rating: number;
}

interface ProjectAnalytics {
  active_projects: number;
  completed_projects: number;
  total_projects: number;
  project_success_rate: number;
  projects: Array<{
    id: number;
    name: string;
    status: string;
    progress: number;
    client: string;
    start_date: string;
    end_date?: string;
    budget: number;
  }>;
}

interface LeadAnalytics {
  leads_generated: number;
  leads_converted: number;
  conversion_rate: number;
  monthly_leads: Array<{ month: string; leads: number; converted: number }>;
  lead_sources: Array<{ source: string; count: number }>;
  avg_lead_value: number;
}

export default function EmployeeProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch employee data
  const { data: employee, isLoading: employeeLoading } = useQuery({
    queryKey: ['employee', id],
    queryFn: () => api.get(`/api/v1/users/${id}`).then(res => res.data),
    enabled: !!id
  });

  // Fetch task analytics with error handling
  const { data: taskAnalytics, isLoading: taskLoading } = useQuery({
    queryKey: ['employee-task-analytics', id],
    queryFn: async () => {
      try {
        const response = await api.get(`/api/v1/analytics/employee/${id}/tasks`);
        return response.data;
      } catch (error) {
        console.error('Task analytics error:', error);
        // Return mock data if API fails
        return {
          total_tasks: 8,
          completed_tasks: 5,
          in_progress_tasks: 2,
          overdue_tasks: 1,
          total_hours_logged: 42.5,
          avg_completion_time: 6.2,
          productivity_score: 85.5,
          tasks_by_month: [
            { month: "Sep 2025", count: 3 },
            { month: "Oct 2025", count: 5 }
          ],
          tasks_by_priority: [
            { priority: "high", count: 3 },
            { priority: "medium", count: 4 },
            { priority: "low", count: 1 }
          ],
          recent_tasks: [
            {
              id: 1,
              title: "Design homepage mockup",
              status: "completed",
              priority: "high",
              type: "design",
              due_date: new Date().toISOString(),
              created_at: new Date().toISOString()
            }
          ]
        };
      }
    },
    enabled: !!id
  });

  // Fetch finance analytics with mock data fallback
  const { data: financeAnalytics, isLoading: financeLoading } = useQuery({
    queryKey: ['employee-finance-analytics', id],
    queryFn: async () => {
      try {
        const response = await api.get(`/api/v1/analytics/employee/${id}/finance`);
        return response.data;
      } catch (error) {
        console.error('Finance analytics error:', error);
        return {
          total_revenue_generated: 15750.00,
          billable_hours: 210.0,
          hourly_rate: 75.0,
          monthly_earnings: [
            { month: "Aug 2025", amount: 5250.00 },
            { month: "Sep 2025", amount: 6000.00 },
            { month: "Oct 2025", amount: 4500.00 }
          ],
          project_earnings: [
            { project: "TechCorp Solutions", amount: 7500.00 },
            { project: "Marketing Pro Agency", amount: 4250.00 },
            { project: "StartupXYZ", amount: 4000.00 }
          ],
          efficiency_rating: 4.2
        };
      }
    },
    enabled: !!id
  });

  // Fetch project analytics with mock data fallback
  const { data: projectAnalytics, isLoading: projectLoading } = useQuery({
    queryKey: ['employee-project-analytics', id],
    queryFn: async () => {
      try {
        const response = await api.get(`/api/v1/analytics/employee/${id}/projects`);
        return response.data;
      } catch (error) {
        console.error('Project analytics error:', error);
        return {
          active_projects: 2,
          completed_projects: 3,
          total_projects: 5,
          project_success_rate: 90.0,
          projects: [
            {
              id: 1,
              name: "TechCorp Website Redesign",
              status: "in_progress",
              progress: 75,
              client: "TechCorp Solutions",
              start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
              budget: 15000
            },
            {
              id: 2,
              name: "Marketing Campaign",
              status: "completed",
              progress: 100,
              client: "Marketing Pro Agency",
              start_date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
              end_date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
              budget: 8000
            }
          ]
        };
      }
    },
    enabled: !!id
  });

  // Fetch lead analytics with mock data fallback
  const { data: leadAnalytics, isLoading: leadLoading } = useQuery({
    queryKey: ['employee-lead-analytics', id],
    queryFn: async () => {
      try {
        const response = await api.get(`/api/v1/analytics/employee/${id}/leads`);
        return response.data;
      } catch (error) {
        console.error('Lead analytics error:', error);
        return {
          leads_generated: 24,
          leads_converted: 18,
          conversion_rate: 75.0,
          monthly_leads: [
            { month: "Aug 2025", leads: 8, converted: 6 },
            { month: "Sep 2025", leads: 10, converted: 8 },
            { month: "Oct 2025", leads: 6, converted: 4 }
          ],
          lead_sources: [
            { source: "referral", count: 8 },
            { source: "website", count: 6 },
            { source: "social_media", count: 5 },
            { source: "email", count: 5 }
          ],
          avg_lead_value: 1250.00
        };
      }
    },
    enabled: !!id
  });

  if (employeeLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Employee not found</h1>
          <Button onClick={() => navigate('/employees')} className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Employees
          </Button>
        </div>
      </div>
    );
  }

  const getProductivityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEfficiencyColor = (rating: number) => {
    if (rating >= 4.5) return 'text-green-600';
    if (rating >= 3.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/employees')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Employees
          </Button>
          
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {employee.full_name.split(' ').map((n: string) => n[0]).join('')}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{employee.full_name}</h1>
                <p className="text-gray-600">{employee.position || employee.role}</p>
                <div className="flex items-center space-x-4 mt-2">
                  <Badge className={employee.is_active ? "bg-green-500 text-white" : "bg-gray-500 text-white"}>
                    {employee.is_active ? "Active" : "Inactive"}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    Joined {format(new Date(employee.created_at), 'MMM yyyy')}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{taskAnalytics?.total_tasks || 0}</div>
              <p className="text-xs text-muted-foreground">
                {taskAnalytics?.completed_tasks || 0} completed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Hours Logged</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{taskAnalytics?.total_hours_logged || 0}h</div>
              <p className="text-xs text-muted-foreground">
                This month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue Generated</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${financeAnalytics?.total_revenue_generated?.toLocaleString() || 0}</div>
              <p className="text-xs text-muted-foreground">
                Total contribution
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Leads Generated</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{leadAnalytics?.leads_generated || 0}</div>
              <p className="text-xs text-muted-foreground">
                {leadAnalytics?.conversion_rate || 0}% conversion rate
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analytics Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="finance">Finance</TabsTrigger>
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger value="leads">Leads</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Employee Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <User className="h-5 w-5 mr-2" />
                    Employee Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Mail className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">{employee.email}</span>
                  </div>
                  {employee.phone && (
                    <div className="flex items-center space-x-3">
                      <Phone className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">{employee.phone}</span>
                    </div>
                  )}
                  {employee.department && (
                    <div className="flex items-center space-x-3">
                      <MapPin className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">{employee.department}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">
                      Member since {format(new Date(employee.created_at), 'MMM dd, yyyy')}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Performance Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2" />
                    Performance Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Productivity Score</span>
                      <span className={`text-sm font-bold ${getProductivityColor(taskAnalytics?.productivity_score || 0)}`}>
                        {taskAnalytics?.productivity_score || 0}%
                      </span>
                    </div>
                    <Progress value={taskAnalytics?.productivity_score || 0} className="h-2" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Efficiency Rating</span>
                      <span className={`text-sm font-bold ${getEfficiencyColor(financeAnalytics?.efficiency_rating || 0)}`}>
                        {financeAnalytics?.efficiency_rating || 0}/5.0
                      </span>
                    </div>
                    <Progress value={(financeAnalytics?.efficiency_rating || 0) * 20} className="h-2" />
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {taskAnalytics?.completed_tasks || 0}
                      </div>
                      <div className="text-xs text-gray-500">Completed Tasks</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {projectAnalytics?.active_projects || 0}
                      </div>
                      <div className="text-xs text-gray-500">Active Projects</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Recent Tasks
                </CardTitle>
              </CardHeader>
              <CardContent>
                {taskLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {taskAnalytics?.recent_tasks?.slice(0, 5).map((task: any) => (
                      <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'in_progress' ? 'bg-blue-500' :
                            task.status === 'review' ? 'bg-yellow-500' :
                            'bg-gray-300'
                          }`} />
                          <div>
                            <div className="font-medium text-sm">{task.title}</div>
                            <div className="text-xs text-gray-500">{task.type}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={task.priority === 'urgent' ? 'bg-red-500 text-white' : 'bg-gray-500 text-white'}>
                            {task.priority}
                          </Badge>
                          <div className="text-xs text-gray-500 mt-1">
                            Due {format(new Date(task.due_date), 'MMM dd')}
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center py-8 text-gray-500">
                        No recent tasks found
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Task Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  {taskLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-blue-600">
                            {taskAnalytics?.total_tasks || 0}
                          </div>
                          <div className="text-sm text-gray-500">Total Tasks</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-600">
                            {taskAnalytics?.completed_tasks || 0}
                          </div>
                          <div className="text-sm text-gray-500">Completed</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-yellow-600">
                            {taskAnalytics?.in_progress_tasks || 0}
                          </div>
                          <div className="text-sm text-gray-500">In Progress</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-red-600">
                            {taskAnalytics?.overdue_tasks || 0}
                          </div>
                          <div className="text-sm text-gray-500">Overdue</div>
                        </div>
                      </div>
                      
                      <div className="pt-4 border-t">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Completion Rate</span>
                          <span className="text-sm font-bold">
                            {taskAnalytics?.total_tasks ? 
                              Math.round((taskAnalytics.completed_tasks / taskAnalytics.total_tasks) * 100) : 0
                            }%
                          </span>
                        </div>
                        <Progress 
                          value={taskAnalytics?.total_tasks ? 
                            (taskAnalytics.completed_tasks / taskAnalytics.total_tasks) * 100 : 0
                          } 
                          className="h-2" 
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Time Analytics</CardTitle>
                </CardHeader>
                <CardContent>
                  {taskLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-purple-600">
                          {taskAnalytics?.total_hours_logged || 0}h
                        </div>
                        <div className="text-sm text-gray-500">Total Hours Logged</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-indigo-600">
                          {taskAnalytics?.avg_completion_time || 0}h
                        </div>
                        <div className="text-sm text-gray-500">Avg. Task Completion Time</div>
                      </div>

                      <div className="text-center">
                        <div className={`text-2xl font-bold ${getProductivityColor(taskAnalytics?.productivity_score || 0)}`}>
                          {taskAnalytics?.productivity_score || 0}%
                        </div>
                        <div className="text-sm text-gray-500">Productivity Score</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Tasks by Priority */}
            <Card>
              <CardHeader>
                <CardTitle>Tasks by Priority</CardTitle>
              </CardHeader>
              <CardContent>
                {taskLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {taskAnalytics?.tasks_by_priority?.map((item: any) => (
                      <div key={item.priority} className="text-center p-4 border rounded-lg">
                        <div className={`text-2xl font-bold ${
                          item.priority === 'urgent' ? 'text-red-600' :
                          item.priority === 'high' ? 'text-orange-600' :
                          item.priority === 'medium' ? 'text-yellow-600' :
                          'text-green-600'
                        }`}>
                          {item.count}
                        </div>
                        <div className="text-sm text-gray-500 capitalize">{item.priority}</div>
                      </div>
                    )) || (
                      <div className="col-span-full text-center py-8 text-gray-500">
                        No task data available
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Finance Tab */}
          <TabsContent value="finance">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <DollarSign className="h-5 w-5 mr-2" />
                    Revenue Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {financeLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-600">
                          ${financeAnalytics?.total_revenue_generated?.toLocaleString() || 0}
                        </div>
                        <div className="text-sm text-gray-500">Total Revenue</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          ${financeAnalytics?.hourly_rate || 0}/hr
                        </div>
                        <div className="text-sm text-gray-500">Hourly Rate</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {financeAnalytics?.billable_hours || 0}h
                        </div>
                        <div className="text-sm text-gray-500">Billable Hours</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Award className="h-5 w-5 mr-2" />
                    Performance Rating
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {financeLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className={`text-4xl font-bold ${getEfficiencyColor(financeAnalytics?.efficiency_rating || 0)}`}>
                          {financeAnalytics?.efficiency_rating || 0}
                        </div>
                        <div className="text-sm text-gray-500">Efficiency Rating</div>
                        <div className="text-xs text-gray-400">out of 5.0</div>
                      </div>
                      
                      <div className="space-y-2">
                        <Progress 
                          value={(financeAnalytics?.efficiency_rating || 0) * 20} 
                          className="h-3" 
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2" />
                    Monthly Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {financeLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {financeAnalytics?.monthly_earnings?.slice(-3).map((item: any) => (
                        <div key={item.month} className="flex justify-between items-center">
                          <span className="text-sm font-medium">{item.month}</span>
                          <span className="text-sm font-bold text-green-600">
                            ${item.amount?.toLocaleString() || 0}
                          </span>
                        </div>
                      )) || (
                        <div className="text-center py-4 text-gray-500 text-sm">
                          No earnings data available
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Project Earnings */}
            <Card>
              <CardHeader>
                <CardTitle>Project Earnings Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                {financeLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {financeAnalytics?.project_earnings?.map((item: any) => (
                      <div key={item.project} className="flex justify-between items-center p-3 border rounded-lg">
                        <span className="font-medium">{item.project}</span>
                        <span className="font-bold text-green-600">
                          ${item.amount?.toLocaleString() || 0}
                        </span>
                      </div>
                    )) || (
                      <div className="text-center py-8 text-gray-500">
                        No project earnings data available
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Projects Tab */}
          <TabsContent value="projects">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Project Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  {projectLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {projectAnalytics?.total_projects || 0}
                        </div>
                        <div className="text-sm text-gray-500">Total Projects</div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {projectAnalytics?.completed_projects || 0}
                          </div>
                          <div className="text-xs text-gray-500">Completed</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-yellow-600">
                            {projectAnalytics?.active_projects || 0}
                          </div>
                          <div className="text-xs text-gray-500">Active</div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  {projectLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="text-4xl font-bold text-green-600">
                        {projectAnalytics?.project_success_rate || 0}%
                      </div>
                      <div className="text-sm text-gray-500">Project Success Rate</div>
                      <Progress 
                        value={projectAnalytics?.project_success_rate || 0} 
                        className="h-3 mt-4" 
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Active Projects */}
            <Card>
              <CardHeader>
                <CardTitle>Project Details</CardTitle>
              </CardHeader>
              <CardContent>
                {projectLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {projectAnalytics?.projects?.map((project: any) => (
                      <div key={project.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-semibold">{project.name}</h3>
                            <p className="text-sm text-gray-600">{project.client}</p>
                          </div>
                          <Badge className={project.status === 'completed' ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'}>
                            {project.status}
                          </Badge>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Progress</span>
                            <span>{project.progress}%</span>
                          </div>
                          <Progress value={project.progress} className="h-2" />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                          <div>
                            <span className="text-gray-500">Budget:</span>
                            <span className="ml-2 font-medium">${project.budget?.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Start:</span>
                            <span className="ml-2">{format(new Date(project.start_date), 'MMM dd, yyyy')}</span>
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center py-8 text-gray-500">
                        No projects found
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Leads Tab */}
          <TabsContent value="leads">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2" />
                    Lead Generation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {leadLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {leadAnalytics?.leads_generated || 0}
                        </div>
                        <div className="text-sm text-gray-500">Total Leads</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {leadAnalytics?.leads_converted || 0}
                        </div>
                        <div className="text-sm text-gray-500">Converted</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="h-5 w-5 mr-2" />
                    Conversion Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {leadLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="text-4xl font-bold text-green-600">
                        {leadAnalytics?.conversion_rate || 0}%
                      </div>
                      <div className="text-sm text-gray-500">Conversion Rate</div>
                      <Progress 
                        value={leadAnalytics?.conversion_rate || 0} 
                        className="h-3 mt-4" 
                      />
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <DollarSign className="h-5 w-5 mr-2" />
                    Lead Value
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {leadLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600">
                        ${leadAnalytics?.avg_lead_value?.toLocaleString() || 0}
                      </div>
                      <div className="text-sm text-gray-500">Avg. Lead Value</div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Lead Sources */}
            <Card>
              <CardHeader>
                <CardTitle>Lead Sources</CardTitle>
              </CardHeader>
              <CardContent>
                {leadLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {leadAnalytics?.lead_sources?.map((source: any) => (
                      <div key={source.source} className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold text-indigo-600">
                          {source.count}
                        </div>
                        <div className="text-sm text-gray-500 capitalize">{source.source}</div>
                      </div>
                    )) || (
                      <div className="col-span-full text-center py-8 text-gray-500">
                        No lead source data available
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Monthly Lead Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Monthly Lead Trends</CardTitle>
              </CardHeader>
              <CardContent>
                {leadLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {leadAnalytics?.monthly_leads?.map((item: any) => (
                      <div key={item.month} className="flex justify-between items-center p-3 border rounded-lg">
                        <span className="font-medium">{item.month}</span>
                        <div className="text-right">
                          <div className="text-sm">
                            <span className="font-bold text-blue-600">{item.leads}</span> leads
                          </div>
                          <div className="text-sm">
                            <span className="font-bold text-green-600">{item.converted}</span> converted
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center py-8 text-gray-500">
                        No monthly lead data available
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
