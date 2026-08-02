import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:zopic_photos_app/features/competition/domain/models/photo_model.dart';

final photoRepositoryProvider = Provider<PhotoRepository>((ref) {
  return MockPhotoRepository();
});

abstract class PhotoRepository {
  Future<List<Photo>> searchBySelfie();
  Future<List<Photo>> searchByBib(String bibNumber);
  Future<List<Photo>> getAllPhotos();
}

class MockPhotoRepository implements PhotoRepository {
  // Generate fake data
  List<Photo> _generateMockPhotos(int count, {String? tag}) {
    return List.generate(count, (index) {
      return Photo(
        id: 'photo_$index${DateTime.now().millisecondsSinceEpoch}',
        url: 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=1000&q=80',
        watermarkUrl: 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=400&q=30', // Low res for mock watermark
        price: 500.0,
        tags: tag != null ? [tag] : ['Général'],
      );
    });
  }

  @override
  Future<List<Photo>> searchBySelfie() async {
    // Simulate network delay and return 8 photos
    await Future.delayed(const Duration(seconds: 2));
    return _generateMockPhotos(8, tag: 'Selfie Match');
  }

  @override
  Future<List<Photo>> searchByBib(String bibNumber) async {
    // Simulate network delay, error state if bib is '000'
    await Future.delayed(const Duration(seconds: 1));
    if (bibNumber == '000') throw Exception('Erreur de connexion simulée');
    if (bibNumber == '999') return []; // Empty state
    return _generateMockPhotos(5, tag: 'Dossard $bibNumber');
  }

  @override
  Future<List<Photo>> getAllPhotos() async {
    await Future.delayed(const Duration(seconds: 2));
    return _generateMockPhotos(24);
  }
}
