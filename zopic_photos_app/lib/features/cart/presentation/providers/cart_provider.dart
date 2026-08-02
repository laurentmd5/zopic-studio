import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:zopic_photos_app/features/competition/domain/models/photo_model.dart';

class CartState {
  final List<Photo> items;
  
  CartState({this.items = const []});
  
  double get total => items.fold(0, (sum, item) => sum + item.price);
  
  CartState copyWith({List<Photo>? items}) {
    return CartState(items: items ?? this.items);
  }
}

class CartNotifier extends StateNotifier<CartState> {
  CartNotifier() : super(CartState());

  void togglePhoto(Photo photo) {
    if (state.items.any((p) => p.id == photo.id)) {
      state = state.copyWith(items: state.items.where((p) => p.id != photo.id).toList());
    } else {
      state = state.copyWith(items: [...state.items, photo]);
    }
  }

  void clearCart() {
    state = CartState();
  }
}

final cartProvider = StateNotifierProvider<CartNotifier, CartState>((ref) {
  return CartNotifier();
});
