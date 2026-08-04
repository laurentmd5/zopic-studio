import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './authStore';

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ token: null });
  });

  it('should initialize with null token if localstorage is empty', () => {
    expect(useAuthStore.getState().token).toBeNull();
  });

  it('should set token and save to localStorage', () => {
    useAuthStore.getState().setToken('test-token');
    
    expect(useAuthStore.getState().token).toBe('test-token');
    expect(localStorage.getItem('guest-token')).toBe('test-token');
  });

  it('should logout and clear token from localStorage', () => {
    useAuthStore.getState().setToken('test-token');
    useAuthStore.getState().logout();
    
    expect(useAuthStore.getState().token).toBeNull();
    expect(localStorage.getItem('guest-token')).toBeNull();
  });
});
