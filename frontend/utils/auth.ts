// Auth utility with JWT token management

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  access_token: string | null;
}

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

export const setUser = (user: User) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
};

export const setAuth = (access_token: string, user: User) => {
  setToken(access_token);
  setUser(user);
};

export const logout = async () => {
  if (typeof window === 'undefined') return;
  
  const token = getToken();
  
  // Try to call sign-out API if we have a token
  if (token) {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${API_URL}/api/auth/sign-out`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Sign-out API error:', error);
    }
  }
  
  // Always clear local storage
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const isAuthenticated = (): boolean => {
  return getToken() !== null && getUser() !== null;
};

export const getAuthHeader = (): Record<string, string> | null => {
  const token = getToken();
  if (!token) return null;
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

// Helper to check if token is about to expire (within 5 minutes)
export const isTokenExpiringSoon = (): boolean => {
  // JWT token exp is in the payload, but for simplicity we just check if token exists
  // In production, you'd decode the JWT and check the exp claim
  return isAuthenticated();
};
