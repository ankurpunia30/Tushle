import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../lib/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, fullName: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user info
      api.get('/api/v1/auth/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    console.log('Login attempt for:', email);
    const response = await api.post('/api/v1/auth/login', { email, password });
    console.log('Login response:', response.data);
    const { access_token } = response.data;
    
    localStorage.setItem('token', access_token);
    console.log('Token stored:', access_token);
    
    // Get user info
    console.log('Fetching user info...');
    const userResponse = await api.get('/api/v1/auth/me');
    console.log('User info response:', userResponse.data);
    setUser(userResponse.data);
    console.log('User set in state');
  };

  const register = async (email: string, password: string, fullName: string) => {
    // First register the user
    await api.post('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    
    // Then automatically log them in
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};
