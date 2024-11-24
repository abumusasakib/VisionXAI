import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:vision_xai/constants/ipDetails.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class SettingsCubit extends Cubit<SettingsState> {
  final ValueNotifier<Locale> localeNotifier; // Expose localeNotifier
  final GlobalKey materialAppKey = GlobalKey(); // GlobalKey to rebuild MaterialApp

  SettingsCubit()
      : localeNotifier = ValueNotifier(AppLocalizations.supportedLocales.first),
        super(SettingsState(
          ip: '',
          port: '',
          currentLocale: Locale('bn'), // Default to first locale
          availableLanguages: AppLocalizations.supportedLocales,
        ));

  void loadIpAndPort() async {
    var box = await Hive.box('settings');
    // Default if not found
    final ip = box.get("ip") ?? IPDetails.defaultIP;
    final port = box.get("port") ?? IPDetails.defaultPort;

    // Load the persisted locale, default to the current state's locale
    final localeCode = box.get('locale', defaultValue: Locale('bn'));
    final newLocale = AppLocalizations.supportedLocales.firstWhere(
      (locale) => locale.languageCode == localeCode,
      orElse: () => state.currentLocale,
    );

    localeNotifier.value = newLocale; // Update the ValueNotifier
    emit(state.copyWith(ip: ip, port: port, currentLocale: newLocale));
  }

  Future<void> updateIpAndPort(String ip, String port) async {
    var box = await Hive.openBox('ipBox');
    await box.put("ip", ip);
    await box.put("port", port);

    emit(state.copyWith(ip: ip, port: port));
  }

  void updateLanguage(String languageCode) {
    final newLocale = Locale(languageCode);

    // Persist the choice
    Hive.box('settings').put('locale', languageCode);

    // Update the ValueNotifier
    localeNotifier.value = newLocale;

    // Emit updated locale and trigger app rebuild
    emit(state.copyWith(currentLocale: newLocale));
  }
}
