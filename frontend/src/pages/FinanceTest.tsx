import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

const FinanceTest: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Finance Page Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p>If you can see this, the basic components are working.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default FinanceTest;
