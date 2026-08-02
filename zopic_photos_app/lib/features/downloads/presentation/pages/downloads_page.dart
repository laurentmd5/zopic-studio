import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons/lucide_icons.dart';

class DownloadsPage extends StatefulWidget {
  const DownloadsPage({super.key});

  @override
  State<DownloadsPage> createState() => _DownloadsPageState();
}

class _DownloadsPageState extends State<DownloadsPage> with SingleTickerProviderStateMixin {
  late AnimationController _revealController;
  late Animation<double> _fadeAnimation;

  // Mock bought photos list
  final List<String> _boughtPhotos = [
    'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&w=1000&q=80',
  ];

  @override
  void initState() {
    super.initState();
    // Progressive reveal animation setup (3 seconds duration for the "magic" effect)
    _revealController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );
    _fadeAnimation = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _revealController, curve: Curves.easeInOut),
    );

    // Start reveal animation automatically upon reaching this page
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _revealController.forward();
    });
  }

  @override
  void dispose() {
    _revealController.dispose();
    super.dispose();
  }

  void _downloadAll() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Téléchargement de toutes les photos en HD commencé...')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes Photos (HD)'),
        leading: IconButton(
          icon: const Icon(LucideIcons.home),
          onPressed: () => context.go('/'),
        ),
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.green.withOpacity(0.1),
            child: Row(
              children: [
                const Icon(LucideIcons.checkCircle2, color: Colors.green),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text('Paiement réussi !', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                      Text('Voici vos photos sans filigrane. Le lien expirera dans 24h.', style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _boughtPhotos.length,
              itemBuilder: (context, index) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 24),
                  clipBehavior: Clip.antiAlias,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  child: Column(
                    children: [
                      Stack(
                        children: [
                          // Base HD Image
                          Image.network(
                            _boughtPhotos[index],
                            height: 250,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                          // Fading out Watermark (Progressive Reveal)
                          AnimatedBuilder(
                            animation: _fadeAnimation,
                            builder: (context, child) {
                              return Opacity(
                                opacity: _fadeAnimation.value,
                                child: Container(
                                  height: 250,
                                  width: double.infinity,
                                  color: Colors.black38,
                                  child: Center(
                                    child: Transform.rotate(
                                      angle: -0.5,
                                      child: Text(
                                        'ZOPIC\nPREVIEW',
                                        textAlign: TextAlign.center,
                                        style: TextStyle(
                                          color: Colors.white.withOpacity(0.8),
                                          fontSize: 32,
                                          fontWeight: FontWeight.bold,
                                          shadows: const [Shadow(color: Colors.black, blurRadius: 4)],
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                          // Badge HD (Fades in)
                          Positioned(
                            top: 12,
                            right: 12,
                            child: AnimatedBuilder(
                              animation: _revealController,
                              builder: (context, child) {
                                return Opacity(
                                  opacity: _revealController.value,
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).colorScheme.primary,
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                    child: const Text('HD', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  ),
                                );
                              },
                            ),
                          )
                        ],
                      ),
                      Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('ZOPIC_0001.JPG', style: TextStyle(fontWeight: FontWeight.bold)),
                            TextButton.icon(
                              onPressed: () {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Téléchargement...')),
                                );
                              },
                              icon: const Icon(LucideIcons.download),
                              label: const Text('Enregistrer'),
                            )
                          ],
                        ),
                      )
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: ElevatedButton.icon(
            onPressed: _downloadAll,
            icon: const Icon(LucideIcons.downloadCloud),
            label: const Text('Tout télécharger (ZIP)'),
          ),
        ),
      ),
    );
  }
}
