import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { getToken, onUnauthorized, setToken } from '@/shared/api';
import { login as loginRequest } from './api';

const LOGIN_KEY = 'attendance.admin.login';

function readLogin(): string | null {
  try {
    return localStorage.getItem(LOGIN_KEY);
  } catch {
    return null;
  }
}

function writeLogin(value: string | null): void {
  try {
    if (value) {
      localStorage.setItem(LOGIN_KEY, value);
    } else {
      localStorage.removeItem(LOGIN_KEY);
    }
  } catch {
  }
}

export interface AuthState {
  isAuthenticated: boolean;
  login: string | null;
  signIn: (login: string, password: string) => Promise<void>;
  signOut: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken);
  const [login, setLogin] = useState<string | null>(readLogin);

  const signOut = useCallback(() => {
    setToken(null);
    writeLogin(null);
    setTokenState(null);
    setLogin(null);
  }, []);

  const signIn = useCallback(async (loginValue: string, password: string) => {
    const result = await loginRequest(loginValue, password);
    setToken(result.access_token);
    writeLogin(result.login);
    setTokenState(result.access_token);
    setLogin(result.login);
  }, []);

  useEffect(() => {
    onUnauthorized(signOut);
    return () => onUnauthorized(null);
  }, [signOut]);

  const value = useMemo<AuthState>(
    () => ({ isAuthenticated: token !== null, login, signIn, signOut }),
    [token, login, signIn, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
