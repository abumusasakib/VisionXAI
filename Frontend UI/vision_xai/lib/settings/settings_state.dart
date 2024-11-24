import 'package:flutter/material.dart';

class SettingsState {
  final String ip;
  final String port;
  final Locale currentLocale; // currentLocale
  final List<Locale> availableLanguages;

  SettingsState({
    required this.ip,
    required this.port,
    required this.currentLocale,
    required this.availableLanguages,
  });

  SettingsState copyWith({
    String? ip,
    String? port,
    Locale? currentLocale, // Accepts a Locale instance
  }) {
    return SettingsState(
      ip: ip ?? this.ip,
      port: port ?? this.port,
      currentLocale: currentLocale ?? this.currentLocale, // Update currentLocale
      availableLanguages: availableLanguages,
    );
  }
}
