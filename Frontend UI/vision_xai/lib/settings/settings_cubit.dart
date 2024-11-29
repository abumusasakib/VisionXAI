import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/constants/ipDetails.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit()
      : super(SettingsState(
          ip: '',
          port: '',
          currentLocale: AppLocalizations.supportedLocales.first,
          availableLanguages: AppLocalizations.supportedLocales,
        )) {
    initializeSettings();
  }

  void initializeSettings() async {
    var box = await Hive.openBox('settings');

    // Load saved values or use defaults
    // Load IP and port from Hive, or set default if not found
    final ip = box.get("ip") ?? IPDetails.defaultIP;
    final port = box.get("port") ?? IPDetails.defaultPort;

    // Load the persisted locale from Hive, default to the current state's locale if not found
    final localeCode =
        box.get('locale', defaultValue: 'bn'); // default 'bn' for Bengali

    // Find the corresponding Locale
    final newLocale = AppLocalizations.supportedLocales.firstWhere(
      (locale) => locale.languageCode == localeCode,
      orElse: () => Locale('bn'), // Fallback to Bengali
    );

    // Emit the updated state with loaded IP, port, and locale
    emit(state.copyWith(
      ip: ip,
      port: port,
      currentLocale: newLocale,
    ));
    debugPrint('Initialized state: ${state.toString()}');
  }

  Future<void> updateIpAndPort(String ip, String port) async {
    var box = await Hive.openBox('settings');
    await box.put("ip", ip);
    await box.put("port", port);

    // Emit updated state with new IP and port
    emit(state.copyWith(ip: ip, port: port));
  }

  void updateLanguage(String languageCode) {
    debugPrint('Updating language to: $languageCode');

    final newLocale = Locale(languageCode);

    if (state.currentLocale == newLocale) {
      debugPrint('Locale is already ${newLocale.languageCode}, skipping emit.');
      return;
    }

    // Persist the language choice in Hive
    Hive.box('settings').put('locale', languageCode);

    // Update the state with the new locale
    emit(state.copyWith(currentLocale: newLocale));

    debugPrint(
        'State emitted with locale: ${state.currentLocale.defaultDisplayLanguage}');
  }
}
