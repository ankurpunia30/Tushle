import React, { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  TrendingDown, 
  Award, 
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Activity
} from 'lucide-react';

interface EmployeePerformance {
  id: number;
  employee_id: number;
  employee_name: string;
  period_start: string;
  period_end: string;
  
  // Task Performance
  total_tasks_assigned: number;
  tasks_completed: number;
  tasks_overdue: number;
  task_completion_rate: number;
  avg_task_completion_time: number | null;
  time_efficiency: number | null;
  
  // Lead Performance
  leads_assigned: number;
  leads_contacted: number;
  leads_qualified: number;
  leads_converted: number;
  lead_conversion_rate: number;
  total_estimated_deal_value: number | null;
  total_actual_deal_value: number | null;
  
  // Meeting Performance
  meetings_scheduled: number;
  meetings_completed: number;
  meetings_no_show: number;
  meeting_completion_rate: number;
  
  // Client Management
  clients_managed: number;
  client_satisfaction_score: number | null;
  
  // Overall Performance
  performance_score: number | null;
  rating: string | null;
  
  created_at: string;
  updated_at: string | null;
}

interface EmployeeStats {
  employee_id: number;
  employee_name: string;
  current_period_performance: EmployeePerformance | null;
  active_tasks: number;
  pending_meetings: number;
  recent_activity_score: number;
  performance_trend: string;
  last_30_days_score: number | null;
}

interface TeamOverview {
  total_employees: number;
  avg_performance_score: number;
  top_performer: string | null;
  employees_needing_attention: string[];
  team_task_completion_rate: number;
  team_lead_conversion_rate: number;
  total_revenue_generated: number;
}

const PerformanceDashboard: React.FC = () => {
  const [teamOverview, setTeamOverview] = useState<TeamOverview | null>(null);
  const [employeeStats, setEmployeeStats] = useState<EmployeeStats[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null);
  const [employeeHistory, setEmployeeHistory] = useState<EmployeePerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000/api/v1';

  // Fetch team overview
  const fetchTeamOverview = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/performance/team-overview`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch team overview');
      }
      
      const data = await response.json();
      setTeamOverview(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // Fetch all employee performance
  const fetchEmployeeStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/performance/employees`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch employee stats');
      }
      
      const data = await response.json();
      setEmployeeStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // Fetch employee performance history
  const fetchEmployeeHistory = async (employeeId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/performance/employee/${employeeId}/performance?months=6`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch employee history');
      }
      
      const data = await response.json();
      setEmployeeHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchTeamOverview(), fetchEmployeeStats()]);
      setLoading(false);
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (selectedEmployee) {
      fetchEmployeeHistory(selectedEmployee);
    }
  }, [selectedEmployee]);

  const getRatingColor = (rating: string | null) => {
    switch (rating) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'satisfactory': return 'text-yellow-600 bg-yellow-100';
      case 'needs_improvement': return 'text-orange-600 bg-orange-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'declining': return <TrendingDown className="w-4 h-4 text-red-600" />;
      default: return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Employee Performance Dashboard</h1>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh Data
        </button>
      </div>

      {/* Team Overview Cards */}
      {teamOverview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Employees</p>
                <p className="text-2xl font-bold text-gray-900">{teamOverview.total_employees}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <Award className="w-8 h-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Performance</p>
                <p className="text-2xl font-bold text-gray-900">{teamOverview.avg_performance_score.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Task Completion</p>
                <p className="text-2xl font-bold text-gray-900">{teamOverview.team_task_completion_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Revenue Generated</p>
                <p className="text-2xl font-bold text-gray-900">${teamOverview.total_revenue_generated.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Performer and Attention Needed */}
      {teamOverview && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performer</h3>
            {teamOverview.top_performer ? (
              <div className="flex items-center">
                <Award className="w-6 h-6 text-yellow-500" />
                <span className="ml-2 text-lg font-medium text-gray-900">{teamOverview.top_performer}</span>
              </div>
            ) : (
              <p className="text-gray-600">No top performer data available</p>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Needs Attention</h3>
            {teamOverview.employees_needing_attention.length > 0 ? (
              <div className="space-y-2">
                {teamOverview.employees_needing_attention.map((employee, index) => (
                  <div key={index} className="flex items-center">
                    <AlertTriangle className="w-5 h-5 text-orange-500" />
                    <span className="ml-2 text-gray-900">{employee}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">All employees performing well!</p>
            )}
          </div>
        </div>
      )}

      {/* Employee Performance List */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Employee Performance</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {employeeStats.map((employee) => (
              <div
                key={employee.employee_id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedEmployee === employee.employee_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedEmployee(
                  selectedEmployee === employee.employee_id ? null : employee.employee_id
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{employee.employee_name}</h4>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-sm text-gray-600">
                          {employee.active_tasks} active tasks
                        </span>
                        <span className="text-sm text-gray-600">
                          {employee.pending_meetings} pending meetings
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="flex items-center">
                        {getTrendIcon(employee.performance_trend)}
                        <span className="ml-1 text-sm font-medium text-gray-900">
                          {employee.last_30_days_score?.toFixed(1)}%
                        </span>
                      </div>
                      <span className="text-xs text-gray-600 capitalize">{employee.performance_trend}</span>
                    </div>
                    
                    {employee.current_period_performance && (
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRatingColor(employee.current_period_performance.rating)}`}>
                        {employee.current_period_performance.rating?.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>

                {/* Detailed Performance Metrics (when selected) */}
                {selectedEmployee === employee.employee_id && employee.current_period_performance && (
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Task Performance */}
                      <div>
                        <h5 className="font-medium text-gray-900 mb-3">Task Performance</h5>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Assigned:</span>
                            <span className="font-medium">{employee.current_period_performance.total_tasks_assigned}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Completed:</span>
                            <span className="font-medium">{employee.current_period_performance.tasks_completed}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Overdue:</span>
                            <span className="font-medium text-red-600">{employee.current_period_performance.tasks_overdue}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Completion Rate:</span>
                            <span className="font-medium">{employee.current_period_performance.task_completion_rate.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Lead Performance */}
                      <div>
                        <h5 className="font-medium text-gray-900 mb-3">Lead Performance</h5>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Assigned:</span>
                            <span className="font-medium">{employee.current_period_performance.leads_assigned}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Contacted:</span>
                            <span className="font-medium">{employee.current_period_performance.leads_contacted}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Converted:</span>
                            <span className="font-medium">{employee.current_period_performance.leads_converted}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Conversion Rate:</span>
                            <span className="font-medium">{employee.current_period_performance.lead_conversion_rate.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Meeting & Revenue */}
                      <div>
                        <h5 className="font-medium text-gray-900 mb-3">Meetings & Revenue</h5>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Meetings:</span>
                            <span className="font-medium">{employee.current_period_performance.meetings_completed}/{employee.current_period_performance.meetings_scheduled}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Meeting Rate:</span>
                            <span className="font-medium">{employee.current_period_performance.meeting_completion_rate.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Revenue:</span>
                            <span className="font-medium">${employee.current_period_performance.total_actual_deal_value?.toLocaleString() || '0'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Performance:</span>
                            <span className="font-medium">{employee.current_period_performance.performance_score?.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Performance History Chart Placeholder */}
                    {employeeHistory.length > 0 && (
                      <div className="mt-6 pt-4 border-t border-gray-200">
                        <h5 className="font-medium text-gray-900 mb-3">Performance History (Last 6 Months)</h5>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                            {employeeHistory.slice(0, 6).map((record) => (
                              <div key={record.id} className="text-center">
                                <div className="font-medium text-gray-900">
                                  {new Date(record.period_start).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                                </div>
                                <div className={`text-lg font-bold ${record.performance_score && record.performance_score >= 80 ? 'text-green-600' : record.performance_score && record.performance_score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                                  {record.performance_score?.toFixed(1)}%
                                </div>
                                <div className="text-xs text-gray-600 capitalize">
                                  {record.rating?.replace('_', ' ')}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
