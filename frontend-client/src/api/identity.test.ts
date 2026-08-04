import { describe, it, expect, vi, Mock } from 'vitest';
import { identityApi } from './identity';
import axios from 'axios';

// Mock axios instance directly where it's used
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
      }))
    }
  }
});

// Re-import the mocked api instance to type it
import * as axiosModule from 'axios';
const mockedApi = (axiosModule.default.create as Mock)();

describe('identityApi', () => {
  it('should get public profile', async () => {
    const mockProfile = { id: 1, slug: 'test-slug' };
    (mockedApi.get as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.getPublicProfile('test-slug');
    expect(result).toEqual(mockProfile);
    expect(mockedApi.get).toHaveBeenCalledWith('/public/athletes/test-slug');
  });

  it('should get slug suggestions', async () => {
    const mockSuggestions = ['slug1', 'slug2'];
    (mockedApi.get as Mock).mockResolvedValueOnce({ data: { suggestions: mockSuggestions } });
    
    const result = await identityApi.getSlugSuggestions('base');
    expect(result).toEqual(mockSuggestions);
    expect(mockedApi.get).toHaveBeenCalledWith('/athletes/slug-suggestions', { params: { base_slug: 'base' } });
  });

  it('should create profile', async () => {
    const mockProfile = { id: 1, slug: 'test' };
    (mockedApi.post as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.createProfile({ slug: 'test' });
    expect(result).toEqual(mockProfile);
    expect(mockedApi.post).toHaveBeenCalledWith('/athletes/me/profile', { slug: 'test' });
  });

  it('should get my profile', async () => {
    const mockProfile = { id: 1, slug: 'me' };
    (mockedApi.get as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.getMyProfile();
    expect(result).toEqual(mockProfile);
    expect(mockedApi.get).toHaveBeenCalledWith('/athletes/me/profile');
  });

  it('should update profile', async () => {
    const mockProfile = { id: 1, slug: 'updated' };
    (mockedApi.put as Mock).mockResolvedValueOnce({ data: mockProfile });
    
    const result = await identityApi.updateProfile({ bio: 'hello' });
    expect(result).toEqual(mockProfile);
    expect(mockedApi.put).toHaveBeenCalledWith('/athletes/me/profile', { bio: 'hello' });
  });
});
