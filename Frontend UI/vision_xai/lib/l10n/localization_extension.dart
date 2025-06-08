import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

extension LocalizationExtension on BuildContext {
  AppLocalizations get tr {
    final localizations = AppLocalizations.of(this);
    if (localizations == null) {
      debugPrint('ERROR: AppLocalizations.of(this) is null');
      debugPrint("Localizations not found for context!");
    }
    return localizations!;
  }

  String get connectionTimeout => AppLocalizations.of(this)!.connectionTimeout;
  String badResponse(String statusCode) =>
      AppLocalizations.of(this)!.badResponse(statusCode);
  String get requestCancelled => AppLocalizations.of(this)!.requestCancelled;
  String get noInternetOrServerUnreachable =>
      AppLocalizations.of(this)!.noInternetOrServerUnreachable;
  String get unknownError => AppLocalizations.of(this)!.unknownError;
}
