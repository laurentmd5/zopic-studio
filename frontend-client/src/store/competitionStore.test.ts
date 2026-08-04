import { describe, it, expect } from 'vitest';
import { useCompetitionStore } from './competitionStore';

describe('competitionStore', () => {
  it('should set competition', () => {
    const comp = { id: 1, name: 'Test' };
    useCompetitionStore.getState().setCompetition(comp);
    expect(useCompetitionStore.getState().competition).toEqual(comp);
  });
});
