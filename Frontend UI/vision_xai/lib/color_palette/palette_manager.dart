import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:palette_generator/palette_generator.dart';
// ignore: unused_import
import 'dart:ui' as ui;
import 'dart:async';

class PaletteManager {
  static const Color fallbackPrimary = Color(0xFF089BB7); // Blue Green
  static const Color fallbackSecondary = Color(0xFF0FC0B8); // Light Sea Green
  static const Color fallbackBackground = Color(0xFFFEFDFC); // White 2

  static Future<Map<String, Color>> generatePalette(ImageProvider image) async {
    try {
      final completer = Completer<ImageInfo>();

      final ImageStream stream = image.resolve(ImageConfiguration.empty);

      final listener = ImageStreamListener((ImageInfo info, bool _) {
        if (!completer.isCompleted) {
          completer.complete(info);
        }
      }, onError: (exception, stackTrace) {
        if (!completer.isCompleted) {
          completer.completeError(exception, stackTrace);
        }
      });

      stream.addListener(listener);

      // Wait for image to be fully loaded
      final imageInfo = await completer.future;

      // Remove the listener to prevent memory leaks
      stream.removeListener(listener);

      // Use the already loaded image
      final PaletteGenerator paletteGenerator =
          await PaletteGenerator.fromImage(imageInfo.image);

      return {
        'primary': kIsWeb
            ? getWebSafeColor(fallbackPrimary)
            : paletteGenerator.dominantColor?.color ?? fallbackPrimary,
        'secondary': kIsWeb
            ? getWebSafeColor(fallbackSecondary)
            : paletteGenerator.lightVibrantColor?.color ?? fallbackSecondary,
        'background': kIsWeb
            ? getWebSafeColor(fallbackBackground)
            : paletteGenerator.lightMutedColor?.color ?? fallbackBackground,
      };
    } catch (e) {
      debugPrint('Palette generation error: $e');
      return {
        'primary': fallbackPrimary,
        'secondary': fallbackSecondary,
        'background': fallbackBackground,
      };
    }
  }

  static Color _ensureWebSafeColor(Color color) {
    // Use round instead of integer division to ensure consistent rounding behavior
    final int r = ((color.red / 51).round() * 51).clamp(0, 255);
    final int g = ((color.green / 51).round() * 51).clamp(0, 255);
    final int b = ((color.blue / 51).round() * 51).clamp(0, 255);

    return Color.fromARGB(255, r, g, b);
  }

  static Color getWebSafeColor(Color color) {
    if (kIsWeb) {
      return _ensureWebSafeColor(color);
    }
    return color;
  }

  static Color getWebSafeColorFromHex(String hexColor) {
    final int colorValue = int.parse(hexColor.replaceFirst('#', '0xFF'));
    final Color color = Color(colorValue);
    return getWebSafeColor(color);
  }
}
