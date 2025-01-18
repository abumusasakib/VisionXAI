import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_nsd/flutter_nsd.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/constants/ipDetails.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class SettingsCubit extends Cubit<SettingsState> {
  final FlutterNsd _flutterNsd = FlutterNsd();
  bool _scanning = false;

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
  Future<void> initializeSettings() async {
    var box = await Hive.openBox('settings');

    // Load saved values or use defaults
    // Load IP and port from Hive, or set default if not found
    final ip = box.get("ip") ?? IPDetails.defaultIP;
    final port = box.get("port") ?? IPDetails.defaultPort;

    final localeCode = box.get('locale', defaultValue: 'bn');
    final newLocale = AppLocalizations.supportedLocales.firstWhere(
      (locale) => locale.languageCode == localeCode,
      orElse: () => const Locale('bn'),
    );

    emit(state.copyWith(ip: ip, port: port, currentLocale: newLocale));

    debugPrint(
          'State emitted with locale: ${state.currentLocale.defaultDisplayLanguage}');

    _startMdnsDiscovery();
  }

  /// Update IP and port and persist in Hive
  Future<void> updateIpAndPort(String ip, String port) async {
    var box = await Hive.openBox('settings');
    await box.put("ip", ip);
    await box.put("port", port);

    // Emit updated state with new IP and port
    emit(state.copyWith(ip: ip, port: port));
  }

  /// Update language preference
  Future<void> updateLanguage(String languageCode) async {
    final newLocale = Locale(languageCode);
    if (state.currentLocale == newLocale) return;

    var box = await Hive.openBox('settings');
    await box.put('locale', languageCode);
    emit(state.copyWith(currentLocale: newLocale));
  }

  /// Start mDNS discovery
  Future<void> _startMdnsDiscovery() async {
    if (_scanning) return;
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
  Future<void> _stopMdnsDiscovery() async {
    if (!_scanning) return;

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
    _stopMdnsDiscovery();
    return super.close();
  }
}
