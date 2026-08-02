import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:go_router/go_router.dart';

class CompetitionPage extends StatefulWidget {
  final String eventId;
  const CompetitionPage({super.key, required this.eventId});

  @override
  State<CompetitionPage> createState() => _EventPageState();
}

class _EventPageState extends State<CompetitionPage> {
  final TextEditingController _bibController = TextEditingController();

  void _searchBySelfie() {
    // Navigate to gallery with 'selfie' query
    context.push('/gallery/selfie');
  }

  void _searchByBib() {
    if (_bibController.text.isNotEmpty) {
      context.push('/gallery/bib:${_bibController.text}');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 250.0,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('Marathon de Dakar 2026', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, textBaseline: TextBaseline.alphabetic, shadows: [Shadow(color: Colors.black45, blurRadius: 4)])),
              background: Stack(
                fit: StackFit.expand,
                children: [
                  Image.network(
                    'https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&w=800&q=80',
                    fit: BoxFit.cover,
                  ),
                  Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [Colors.transparent, Colors.black87],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Comment souhaitez-vous trouver vos photos ?',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  
                  // 1. SELFIE (Bouton Principal Waouh)
                  Container(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF6B8E23), Color(0xFF556B2F)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF6B8E23).withOpacity(0.4),
                          blurRadius: 12,
                          offset: const Offset(0, 6),
                        )
                      ],
                    ),
                    child: ElevatedButton(
                      onPressed: _searchBySelfie,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                        padding: const EdgeInsets.symmetric(vertical: 20),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(LucideIcons.camera, size: 28),
                          SizedBox(width: 12),
                          Text(
                            'Trouver avec un Selfie',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  const Row(
                    children: [
                      Expanded(child: Divider()),
                      Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        child: Text('OU', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                      ),
                      Expanded(child: Divider()),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // 2. DOSSARD
                  TextField(
                    controller: _bibController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      hintText: 'Numéro de dossard',
                      prefixIcon: const Icon(LucideIcons.hash),
                      suffixIcon: IconButton(
                        icon: const Icon(LucideIcons.search),
                        onPressed: _searchByBib,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                      fillColor: theme.colorScheme.surface,
                    ),
                    onSubmitted: (_) => _searchByBib(),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // 3. EQUIPE / CATEGORIE
                  const Text('Par équipe ou catégorie', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ActionChip(label: const Text('Hommes 18-35'), onPressed: () {}),
                      ActionChip(label: const Text('Femmes 18-35'), onPressed: () {}),
                      ActionChip(label: const Text('Vétérans'), onPressed: () {}),
                      ActionChip(label: const Text('Équipe Alpha'), onPressed: () {}),
                    ],
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // 4. PARCOURIR TOUT
                  TextButton.icon(
                    onPressed: () {
                      context.push('/gallery/all');
                    },
                    icon: const Icon(LucideIcons.image),
                    label: const Text('Parcourir toutes les photos de l\'compétition', style: TextStyle(fontSize: 16)),
                    style: TextButton.styleFrom(
                      foregroundColor: theme.colorScheme.secondary,
                    ),
                  ),
                  
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _bibController.dispose();
    super.dispose();
  }
}
