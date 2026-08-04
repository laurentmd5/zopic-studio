import { describe, it, expect } from 'vitest';
import { useSearchStore } from './searchStore';

describe('searchStore', () => {
  it('should update search state', () => {
    useSearchStore.getState().setSearchState('loading');
    expect(useSearchStore.getState().state).toBe('loading');
  });

  it('should update search results', () => {
    const results = [{ id: 1, name: 'Result' }];
    useSearchStore.getState().setResults(results);
    expect(useSearchStore.getState().results).toEqual(results);
  });
});
