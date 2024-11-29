import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

class SettingsState extends Equatable {
  final String ip;
  final String port;
  final Locale currentLocale;
  final List<Locale> availableLanguages;

  const SettingsState({
    required this.ip,
    required this.port,
    required this.currentLocale,
    required this.availableLanguages,
  });

  // Override the `props` getter for Equatable comparison
  @override
  List<Object?> get props => [ip, port, currentLocale, availableLanguages];

  // Implement the `copyWith` pattern
  SettingsState copyWith({
    String? ip,
    String? port,
    Locale? currentLocale,
    List<Locale>? availableLanguages,
  }) {
    return SettingsState(
      ip: ip ?? this.ip,
      port: port ?? this.port,
      currentLocale: currentLocale ?? this.currentLocale,
      availableLanguages: availableLanguages ?? this.availableLanguages,
    );
  }

  @override
  String toString() =>
      'SettingsState(ip: $ip, port: $port, currentLocale: $currentLocale, availableLanguages: $availableLanguages)';
}
