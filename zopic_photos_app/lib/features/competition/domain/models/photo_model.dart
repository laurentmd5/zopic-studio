class Photo {
  final String id;
  final String url;
  final String watermarkUrl;
  final double price;
  final List<String> tags;

  Photo({
    required this.id,
    required this.url,
    required this.watermarkUrl,
    required this.price,
    required this.tags,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      id: json['id'],
      url: json['url'],
      watermarkUrl: json['watermarkUrl'],
      price: json['price'].toDouble(),
      tags: List<String>.from(json['tags'] ?? []),
    );
  }
}
