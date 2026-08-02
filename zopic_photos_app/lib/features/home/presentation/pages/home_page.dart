import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ZoPic Photos')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Trouvez vos photos sportives en un clin d\'œil'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Simulation d'un scan QR Code
                GoRouter.of(context).go('/competition/123');
              },
              child: const Text('Simuler un Scan QR (Aller à la compétition)'),
            )
          ],
        ),
      ),
    );
  }
}
