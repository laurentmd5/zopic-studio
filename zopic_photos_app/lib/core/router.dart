import 'package:go_router/go_router.dart';
import '../features/home/presentation/pages/home_page.dart';
import '../features/competition/presentation/pages/competition_page.dart';
import '../features/competition/presentation/pages/gallery_page.dart';
import '../features/cart/presentation/pages/checkout_page.dart';
import '../features/downloads/presentation/pages/downloads_page.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/competition/:id',
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return CompetitionPage(eventId: id);
      },
    ),
    GoRoute(
      path: '/gallery/:query',
      builder: (context, state) {
        final query = state.pathParameters['query']!;
        return GalleryPage(query: query);
      },
    ),
    GoRoute(
      path: '/checkout',
      builder: (context, state) => const CheckoutPage(),
    ),
    GoRoute(
      path: '/downloads',
      builder: (context, state) => const DownloadsPage(),
    ),
  ],
);
