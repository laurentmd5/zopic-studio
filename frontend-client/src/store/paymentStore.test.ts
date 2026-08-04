import { describe, it, expect } from 'vitest';
import { usePaymentStore } from './paymentStore';

describe('paymentStore', () => {
  it('should initialize with idle status', () => {
    expect(usePaymentStore.getState().status).toBe('idle');
  });

  it('should update payment status', () => {
    usePaymentStore.getState().setStatus('success');
    expect(usePaymentStore.getState().status).toBe('success');
  });
});
