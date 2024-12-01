import 'package:arb_utils/arb_utils_flutter.dart';
import 'package:arb_utils/state_managers/l10n_provider.dart';
import 'package:flutter/material.dart';
import 'package:locale_names/locale_names.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class CustomLanguageSelectorDropdown extends StatelessWidget {
  CustomLanguageSelectorDropdown({
    super.key,

    /// Provided the [AppLocalizations.supportedLocales]
    required this.supportedLocales,

    /// A callback to be called when the user selects a language.
    this.languageChangeHandler,

    /// Optionally, a custom icon
    this.icon,

    /// Optionally pass a provider to manage localization
    this.provider,
  });

  final ProviderL10n? provider;
  final List<Locale> supportedLocales;
  final Icon? icon;
  final LanguageChangeHandler? languageChangeHandler;

  /// Get the display name of a language from a Locale instance
  String getLanguageNameFromLocale(Locale locale) {
    return locale.nativeDisplayLanguage;
  }

  /// Handler for language change
  void languageChangedHandler(String? localeId) {
    if (localeId == null) return;

    // Create a Locale instance from the language tag
    var locale = Locale(localeId);

    // Trigger callback if provided
    if (languageChangeHandler != null) {
      languageChangeHandler!(locale);
    }

    // Update the ProviderL10n instance if available
    provider?.locale = locale;
  }

  /// Build a dropdown menu item for each locale
  DropdownMenuItem<String> _buildMenuItem(Locale locale) {
    return DropdownMenuItem<String>(
      value: locale.toLanguageTag(),
      child: Text(
        getLanguageNameFromLocale(locale),
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Flexible(
      fit: FlexFit.loose, // Constrain the width of DropdownButton
      child: DropdownButton<String>(
        icon: icon ?? const Icon(Icons.language), // Default icon or custom one
        value: AppLocalizations.of(context)?.localeName,
        items: supportedLocales.map(_buildMenuItem).toList(),
        onChanged: languageChangedHandler,
        isExpanded: true, // Adjust width
        elevation: 16,
        style: const TextStyle(color: Colors.black),
        dropdownColor: Colors.white,
      ),
    );
  }
}
