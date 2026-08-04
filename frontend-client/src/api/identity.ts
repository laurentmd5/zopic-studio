import axios from 'axios';
const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' });

export interface AthleteStatistics {
  competitions: number;
  photos: number;
  disciplines: number;
  albums: number;
  photographers: number;
  active_since_year: number | null;
}

export interface PublicAthleteProfile {
  id: number;
  slug: string;
  is_public: string;
  bio: string | null;
  club: string | null;
  nationality: string | null;
  birth_date: string | null;
  sport_attributes: Record<string, any>;
  theme_color: string;
  is_verified: boolean;
  profile_photo_url: string | null;
  cover_photo_url: string | null;
  favorite_photo_id: number | null;
  statistics: AthleteStatistics;
}

export const identityApi = {
  getPublicProfile: async (slug: string): Promise<PublicAthleteProfile> => {
    const response = await api.get(`/public/athletes/${slug}`);
    return response.data;
  },

  getSlugSuggestions: async (baseSlug: string): Promise<string[]> => {
    const response = await api.get(`/athletes/slug-suggestions`, { params: { base_slug: baseSlug } });
    return response.data.suggestions;
  },

  createProfile: async (data: any): Promise<PublicAthleteProfile> => {
    const response = await api.post(`/athletes/me/profile`, data);
    return response.data;
  },

  getMyProfile: async (): Promise<PublicAthleteProfile> => {
    const response = await api.get(`/athletes/me/profile`);
    return response.data;
  },

  updateProfile: async (data: any): Promise<PublicAthleteProfile> => {
    const response = await api.put(`/athletes/me/profile`, data);
    return response.data;
  }
};
