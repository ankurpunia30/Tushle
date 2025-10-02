import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Plus, FileText, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

interface InvoiceStats {
  total_invoices: number;
  paid_invoices: number;
  overdue_invoices: number;
  pending_invoices: number;
  total_revenue: number;
  overdue_amount: number;
}

const Finance: React.FC = () => {
  // Mock data for testing
  const stats: InvoiceStats = {
    total_invoices: 25,
    paid_invoices: 18,
    overdue_invoices: 3,
    pending_invoices: 4,
    total_revenue: 45750.00,
    overdue_amount: 5200.00
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Finance</h1>
          <p className="text-gray-600 mt-1">
            Manage invoices, payments, and financial overview
          </p>
        </div>
        
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Invoice
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <FileText className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${stats.total_revenue.toFixed(2)}</div>
            <p className="text-xs text-gray-600">
              From {stats.paid_invoices} paid invoices
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending_invoices}</div>
            <p className="text-xs text-gray-600">
              Awaiting payment
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue Amount</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ${stats.overdue_amount.toFixed(2)}
            </div>
            <p className="text-xs text-gray-600">
              {stats.overdue_invoices} overdue invoices
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Invoices</CardTitle>
            <FileText className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_invoices}</div>
            <p className="text-xs text-gray-600">
              All-time invoices
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Sample Invoice List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Invoices</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">INV-2024-001</p>
                <p className="text-sm text-gray-600">TechCorp Solutions</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="font-medium">$7,500.00</p>
                  <p className="text-sm text-gray-600">Due: Oct 15, 2024</p>
                </div>
                <Badge variant="success">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Paid
                </Badge>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">INV-2024-002</p>
                <p className="text-sm text-gray-600">Marketing Pro Agency</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="font-medium">$3,200.00</p>
                  <p className="text-sm text-gray-600">Due: Nov 01, 2024</p>
                </div>
                <Badge variant="default">
                  <Clock className="h-3 w-3 mr-1" />
                  Sent
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Finance;
