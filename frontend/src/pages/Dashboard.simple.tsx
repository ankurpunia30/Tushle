import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh' }}>
      <h1 style={{ color: 'black', fontSize: '24px', marginBottom: '20px' }}>
        🎉 Dashboard Loaded Successfully!
      </h1>
      <div style={{ backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ color: 'black', fontSize: '18px' }}>Welcome to Tushle</h2>
        <p style={{ color: '#666', marginTop: '10px' }}>
          If you can see this, the React app is working correctly after login.
        </p>
        <div style={{ marginTop: '20px' }}>
          <p style={{ color: 'black' }}>✅ Authentication: Working</p>
          <p style={{ color: 'black' }}>✅ Routing: Working</p>
          <p style={{ color: 'black' }}>✅ Components: Working</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
