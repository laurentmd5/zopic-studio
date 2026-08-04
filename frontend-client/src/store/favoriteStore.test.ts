import { describe, it, expect, beforeEach } from 'vitest';
import { useFavoriteStore } from './favoriteStore';

describe('favoriteStore', () => {
  beforeEach(() => {
    localStorage.clear();
    // clear the store manually for tests
    useFavoriteStore.setState({ favorites: [], sessionId: 'test-session-id' });
  });

  it('should initialize with empty favorites', () => {
    expect(useFavoriteStore.getState().favorites).toEqual([]);
    expect(useFavoriteStore.getState().sessionId).toBeTruthy();
  });

  it('should toggle favorite (add and remove)', () => {
    const photo = { id: 1, url: 'img1.jpg' };
    
    // Add
    useFavoriteStore.getState().toggleFavorite(photo);
    expect(useFavoriteStore.getState().favorites).toHaveLength(1);
    expect(useFavoriteStore.getState().favorites[0]).toEqual(photo);
    expect(useFavoriteStore.getState().isFavorite(1)).toBe(true);

    // Remove (toggle again)
    useFavoriteStore.getState().toggleFavorite(photo);
    expect(useFavoriteStore.getState().favorites).toHaveLength(0);
    expect(useFavoriteStore.getState().isFavorite(1)).toBe(false);
  });

  it('should remove multiple favorites', () => {
    const p1 = { id: 1 };
    const p2 = { id: 2 };
    const p3 = { id: 3 };
    
    useFavoriteStore.setState({ favorites: [p1, p2, p3] });
    
    useFavoriteStore.getState().removeFavorites([1, 3]);
    
    expect(useFavoriteStore.getState().favorites).toHaveLength(1);
    expect(useFavoriteStore.getState().favorites[0]).toEqual(p2);
  });
});
