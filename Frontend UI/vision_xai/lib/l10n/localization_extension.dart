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
}
