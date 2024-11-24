import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:locale_names/locale_names.dart';

class LanguageSettings extends StatelessWidget {
  const LanguageSettings({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<SettingsCubit, SettingsState>(
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: Text(context.tr.languageSettings),
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(context.tr.selectLanguage, style: const TextStyle(fontSize: 18)),
                const SizedBox(height: 16),
                DropdownButton<Locale>(
                  value: state.currentLocale,
                  items: state.availableLanguages.map((locale) {
                    return DropdownMenuItem(
                      value: locale,
                      child: Text(locale.defaultDisplayLanguage),
                    );
                  }).toList(),
                  onChanged: (locale) {
                    if (locale != null) {
                      context.read<SettingsCubit>().updateLanguage(locale.languageCode);
                    }
                    Navigator.of(context).pop();
                  },
                  isExpanded: true,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
