import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Clients from './pages/Clients';
import ClientDetail from './pages/ClientDetail';
import ClientPortal from './pages/ClientPortal';
import Finance from './pages/Finance';
import Leads from './pages/Leads';
import Tasks from './pages/Tasks';
import ContentEngine from './pages/ContentEngine';
import Reports from './pages/Reports';
import AIScriptGenerator from './pages/AIScriptGenerator';
import EmployeeManagement from './pages/EmployeeManagement';
import EmployeeProfile from './pages/EmployeeProfile';
import Layout from './components/Layout';
import './index.css';

const queryClient = new QueryClient();

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            {/* Public route for client portal */}
            <Route path="/portal/:clientId" element={<ClientPortal />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/clients" element={<Clients />} />
                      <Route path="/clients/:id" element={<ClientDetail />} />
                      <Route path="/finance" element={<Finance />} />
                      <Route path="/leads" element={<Leads />} />
                      <Route path="/tasks" element={<Tasks />} />
                      <Route path="/employees" element={<EmployeeManagement />} />
                      <Route path="/employees/:id" element={<EmployeeProfile />} />
                      <Route path="/content" element={<ContentEngine />} />
                      <Route path="/ai-script-generator" element={<AIScriptGenerator />} />
                      <Route path="/reports" element={<Reports />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
