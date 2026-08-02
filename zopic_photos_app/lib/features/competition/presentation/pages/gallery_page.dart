import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../domain/models/photo_model.dart';
import '../../data/repositories/photo_repository.dart';
import '../../../cart/presentation/providers/cart_provider.dart';
import 'package:go_router/go_router.dart';

// Provider to fetch photos based on search query
final galleryProvider = FutureProvider.family<List<Photo>, String>((ref, query) async {
  final repo = ref.watch(photoRepositoryProvider);
  if (query == 'selfie') {
    return repo.searchBySelfie();
  } else if (query.startsWith('bib:')) {
    return repo.searchByBib(query.split(':')[1]);
  } else {
    return repo.getAllPhotos();
  }
});

class GalleryPage extends ConsumerWidget {
  final String query; // 'selfie', 'bib:123', 'all'
  const GalleryPage({super.key, required this.query});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final photosAsyncValue = ref.watch(galleryProvider(query));
    final cart = ref.watch(cartProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Résultats'),
        actions: [
          IconButton(
            icon: const Icon(LucideIcons.shoppingBag),
            onPressed: () {
              context.push('/checkout');
            },
          )
        ],
      ),
      body: photosAsyncValue.when(
        data: (photos) {
          if (photos.isEmpty) {
            return _buildEmptyState(context);
          }
          return _buildGrid(context, ref, photos);
        },
        loading: () => _buildLoadingState(),
        error: (err, stack) => _buildErrorState(context, err.toString()),
      ),
      floatingActionButton: cart.items.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: () {
                context.push('/checkout');
              },
              backgroundColor: Theme.of(context).colorScheme.primary,
              icon: const Icon(LucideIcons.shoppingCart, color: Colors.white),
              label: Text(
                'Voir le panier (${cart.items.length}) - ${cart.total.toInt()} FCFA',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            )
          : null,
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }

  Widget _buildGrid(BuildContext context, WidgetRef ref, List<Photo> photos) {
    return MasonryGridView.count(
      crossAxisCount: 2,
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      padding: const EdgeInsets.all(8).copyWith(bottom: 100), // Padding for FAB
      itemCount: photos.length,
      itemBuilder: (context, index) {
        final photo = photos[index];
        final isSelected = ref.watch(cartProvider).items.any((p) => p.id == photo.id);

        return GestureDetector(
          onTap: () {
            ref.read(cartProvider.notifier).togglePhoto(photo);
          },
          child: Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  photo.watermarkUrl,
                  fit: BoxFit.cover,
                  loadingBuilder: (context, child, progress) {
                    if (progress == null) return child;
                    return Container(
                      height: 200,
                      color: Colors.grey[300],
                      child: const Center(child: CircularProgressIndicator()),
                    );
                  },
                ),
              ),
              // Watermark overlay simulation
              Positioned.fill(
                child: Center(
                  child: Transform.rotate(
                    angle: -0.5,
                    child: Text(
                      'ZOPIC\nPREVIEW',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.5),
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        shadows: const [Shadow(color: Colors.black, blurRadius: 4)],
                      ),
                    ),
                  ),
                ),
              ),
              // Selection Checkbox
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isSelected ? Theme.of(context).colorScheme.primary : Colors.white.withOpacity(0.8),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(4.0),
                    child: Icon(
                      isSelected ? LucideIcons.check : LucideIcons.plus,
                      size: 20,
                      color: isSelected ? Colors.white : Colors.black54,
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          CircularProgressIndicator(),
          SizedBox(height: 24),
          Text('Analyse des photos en cours...', style: TextStyle(fontSize: 16)),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(LucideIcons.cameraOff, size: 64, color: Colors.grey),
            const SizedBox(height: 24),
            const Text(
              'Aucune photo trouvée',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            const Text(
              'Nous n\'avons pas trouvé de photos correspondantes. Essayez avec un autre mode de recherche.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 32),
            OutlinedButton(
              onPressed: () => context.pop(),
              child: const Text('Retour à la recherche'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(LucideIcons.alertCircle, size: 64, color: Colors.red),
            const SizedBox(height: 24),
            const Text('Oups !', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text(error, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () => context.pop(),
              child: const Text('Réessayer'),
            ),
          ],
        ),
      ),
    );
  }
}
