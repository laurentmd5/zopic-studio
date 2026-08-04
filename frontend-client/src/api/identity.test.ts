import { describe, it, expect, vi, Mock } from 'vitest';
import { identityApi } from './identity';
const { mockApi } = vi.hoisted(() => ({
  mockApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  }
}));

vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => mockApi)
    }
  }
});

describe('identityApi', () => {
  it('should get public profile', async () => {
    const mockProfile = { id: 1, slug: 'test-slug' };
    (mockApi.get as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.getPublicProfile('test-slug');
    expect(result).toEqual(mockProfile);
    expect(mockApi.get).toHaveBeenCalledWith('/public/athletes/test-slug');
  });

  it('should get slug suggestions', async () => {
    const mockSuggestions = ['slug1', 'slug2'];
    (mockApi.get as Mock).mockResolvedValueOnce({ data: { suggestions: mockSuggestions } });
    
    const result = await identityApi.getSlugSuggestions('base');
    expect(result).toEqual(mockSuggestions);
    expect(mockApi.get).toHaveBeenCalledWith('/athletes/slug-suggestions', { params: { base_slug: 'base' } });
  });

  it('should create profile', async () => {
    const mockProfile = { id: 1, slug: 'test' };
    (mockApi.post as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.createProfile({ slug: 'test' });
    expect(result).toEqual(mockProfile);
    expect(mockApi.post).toHaveBeenCalledWith('/athletes/me/profile', { slug: 'test' });
  });

  it('should get my profile', async () => {
    const mockProfile = { id: 1, slug: 'me' };
    (mockApi.get as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.getMyProfile();
    expect(result).toEqual(mockProfile);
    expect(mockApi.get).toHaveBeenCalledWith('/athletes/me/profile');
  });

  it('should update profile', async () => {
    const mockProfile = { id: 1, slug: 'updated' };
    (mockApi.put as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.updateProfile({ bio: 'hello' });
    expect(result).toEqual(mockProfile);
    expect(mockApi.put).toHaveBeenCalledWith('/athletes/me/profile', { bio: 'hello' });
  });
});
