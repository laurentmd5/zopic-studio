import { describe, it, expect } from 'vitest';
import { useDownloadStore } from './downloadStore';

describe('downloadStore', () => {
  it('should set purchased photos', () => {
    const photos = [{ id: 1, url: 'img.jpg' }];
    useDownloadStore.getState().setPurchasedPhotos(photos);
    expect(useDownloadStore.getState().purchasedPhotos).toEqual(photos);
  });
});
