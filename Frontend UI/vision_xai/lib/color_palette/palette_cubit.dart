import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:vision_xai/color_palette/palette_manager.dart';
import 'package:vision_xai/color_palette/palette_state.dart';

class PaletteCubit extends Cubit<PaletteState> {
  PaletteCubit()
      : super(PaletteState(
          primaryColor: const Color(0xFF089BB7), // Default Blue Green
          secondaryColor: const Color(0xFF0FC0B8), // Default Light Sea Green
          backgroundColor: const Color(0xFFFEFDFC), // Default White
        ));

  Future<void> updateColors() async {
    final palette = await PaletteManager.generatePalette(
        const AssetImage('assets/icon/icon.png'));

    emit(PaletteState(
      primaryColor: palette['primary'] ?? const Color(0xFF089BB7),
      secondaryColor: palette['secondary'] ?? const Color(0xFF0FC0B8),
      backgroundColor: palette['background'] ?? const Color(0xFFFEFDFC),
    ));
  }
}
