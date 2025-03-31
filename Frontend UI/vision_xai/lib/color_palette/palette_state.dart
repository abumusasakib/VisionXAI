import 'dart:ui';

class PaletteState {
  final Color primaryColor;
  final Color secondaryColor;
  final Color backgroundColor;

  PaletteState({
    required this.primaryColor,
    required this.secondaryColor,
    required this.backgroundColor,
  });

  PaletteState copyWith({
    Color? primaryColor,
    Color? secondaryColor,
    Color? backgroundColor,
  }) {
    return PaletteState(
      primaryColor: primaryColor ?? this.primaryColor,
      secondaryColor: secondaryColor ?? this.secondaryColor,
      backgroundColor: backgroundColor ?? this.backgroundColor,
    );
  }
}