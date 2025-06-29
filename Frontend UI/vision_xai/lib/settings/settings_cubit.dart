import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_nsd/flutter_nsd.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/constants/ip_details.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

/// Cubit responsible for managing application settings, including IP/port
/// and language preferences, with mDNS discovery for automatic server detection.
class SettingsCubit extends Cubit<SettingsState> {
  /// Instance of NSD (Network Service Discovery) for mDNS discovery.
  final FlutterNsd _flutterNsd = FlutterNsd();

  /// Flag to prevent multiple concurrent mDNS scans.
  bool _scanning = false;

  /// Initializes the [SettingsCubit] with a default state.
  ///
  /// The initial state sets the current locale to the first supported locale
  /// and provides all supported locales as available languages.
  SettingsCubit()
      : super(SettingsState(
          ip: '',
          port: '',
          currentLocale: AppLocalizations.supportedLocales.first,
          availableLanguages: AppLocalizations.supportedLocales,
        )) {
    initializeSettings();
  }

  /// Initialize settings and start mDNS discovery
  /// Initializes settings by loading saved preferences from Hive and starts mDNS discovery.
  ///
  /// - Retrieves saved IP and port, falling back to [IPDetails.defaultIP] and [IPDetails.defaultPort].
  /// - Loads the saved locale, defaulting to 'bn' (Bengali) if not found.
  /// - Emits a new state with the loaded settings.
  /// - Initiates [_startMdnsDiscovery] to find available services on the local network.
  Future<void> initializeSettings() async {
    var box = await Hive.openBox('settings');

    // Load saved values or use defaults
    // Load IP and port from Hive, or set default if not found
    final ip = box.get("ip") ?? IPDetails.defaultIP;
    final port = box.get("port") ?? IPDetails.defaultPort;

    final localeCode = box.get('locale', defaultValue: 'bn');
    final newLocale = AppLocalizations.supportedLocales.firstWhere(
      (locale) => locale.languageCode == localeCode,
      orElse: () =>
          const Locale('bn'), // Fallback to Bengali if locale not found
    );

    emit(state.copyWith(ip: ip, port: port, currentLocale: newLocale));

    debugPrint(
        'State emitted with locale: ${state.currentLocale.defaultDisplayLanguage}');

    _startMdnsDiscovery();
  }

  /// Update IP and port and persist in Hive
  /// Updates the IP address and port number and persists them to Hive.
  ///
  /// Emits a new state reflecting the updated IP and port.
  ///
  /// [ip]: The new IP address.
  /// [port]: The new port number.
  Future<void> updateIpAndPort(String ip, String port) async {
    var box = await Hive.openBox('settings');
    await box.put("ip", ip);
    await box.put("port", port);

    // Emit updated state with new IP and port
    emit(state.copyWith(ip: ip, port: port));
  }

  /// Update language preference
  /// Updates the application's language preference and persists it to Hive.
  ///
  /// Only updates if the [languageCode] is different from the current locale.
  /// Emits a new state with the updated locale.
  ///
  /// [languageCode]: The language code (e.g., 'en', 'bn') for the new locale.
  Future<void> updateLanguage(String languageCode) async {
    final newLocale = Locale(languageCode);
    if (state.currentLocale == newLocale) return;

    var box = await Hive.openBox('settings');
    await box.put('locale', languageCode);
    emit(state.copyWith(currentLocale: newLocale));
  }

  /// Start mDNS discovery
  /// Starts mDNS (multicast DNS) discovery to find local network services.
  ///
  /// - Prevents multiple discovery instances from running concurrently.
  /// - Discovers HTTP services (`_http._tcp`).
  /// - Listens for service discovery events (found, resolved, removed).
  /// - If a service is found with a host and port, it updates the IP and port settings.
  Future<void> _startMdnsDiscovery() async {
    if (_scanning) return; // Do not start if already scanning

    _scanning = true;

    try {
      await _flutterNsd.discoverServices('_http._tcp.');

      _flutterNsd.stream.listen(
        (NsdServiceInfo service) {
          if (service.hostname != null && service.port != null) {
            updateIpAndPort(service.hostname!, service.port!.toString());
          }
        },
        onError: (e) {
          if (e is NsdError) {
            debugPrint('mDNS error: ${e.errorCode}');
          } else {
            debugPrint('Unexpected error: $e');
          }
        },
      );
    } catch (e) {
      debugPrint('Failed to start mDNS discovery: $e');
    }
  }

  /// Stop mDNS discovery
  /// Stops the ongoing mDNS discovery.
  ///
  /// - Resets the [_scanning] flag.
  Future<void> _stopMdnsDiscovery() async {
    if (!_scanning) return; // Nothing to stop

    try {
      await _flutterNsd.stopDiscovery();
    } catch (e) {
      debugPrint('Failed to stop mDNS discovery: $e');
    } finally {
      _scanning = false;
    }
  }

  @override
  Future<void> close() {
    _stopMdnsDiscovery(); // Ensure mDNS discovery is stopped when the Cubit is closed
    return super.close();
  }
}
