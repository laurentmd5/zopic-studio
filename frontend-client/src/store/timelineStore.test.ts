import { describe, it, expect, beforeEach, vi } from 'vitest';
import type { Mock } from 'vitest';
import { useTimelineStore } from './timelineStore';
import axios from 'axios';

vi.mock('axios');

describe('timelineStore', () => {
  beforeEach(() => {
    useTimelineStore.setState({
      timeline: [],
      totalCompetitions: 0,
      totalPhotos: 0,
      message: '',
      isLoading: false,
      error: null,
      expandedYears: []
    });
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const state = useTimelineStore.getState();
    expect(state.timeline).toEqual([]);
    expect(state.totalCompetitions).toBe(0);
    expect(state.isLoading).toBe(false);
  });

  it('should toggle year expansion', () => {
    useTimelineStore.getState().toggleYear(2023);
    expect(useTimelineStore.getState().expandedYears).toContain(2023);

    useTimelineStore.getState().toggleYear(2023);
    expect(useTimelineStore.getState().expandedYears).not.toContain(2023);
  });

  it('should fetch timeline successfully', async () => {
    const mockData = {
      timeline: [
        { year: 2024, competitions: [] }
      ],
      total_competitions: 5,
      total_photos: 10,
      message: 'Hello'
    };
    (axios.get as Mock).mockResolvedValueOnce({ data: mockData });

    await useTimelineStore.getState().fetchTimeline('test-session');
    
    const state = useTimelineStore.getState();
    expect(state.timeline).toEqual(mockData.timeline);
    expect(state.totalCompetitions).toBe(5);
    expect(state.totalPhotos).toBe(10);
    expect(state.message).toBe('Hello');
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    // 2024 should be expanded by default since it's the only one
    expect(state.expandedYears).toContain(2024);
  });

  it('should handle fetch timeline error', async () => {
    (axios.get as Mock).mockRejectedValueOnce(new Error('Network error'));

    await useTimelineStore.getState().fetchTimeline('test-session');
    
    const state = useTimelineStore.getState();
    expect(state.isLoading).toBe(false);
    expect(state.error).toBe('Network error');
  });
});
