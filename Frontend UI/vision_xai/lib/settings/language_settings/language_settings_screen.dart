import 'package:arb_utils/state_managers/l10n_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/routes/app_routes.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:vision_xai/widgets/custom_language_selector_dropdown.dart';

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
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(context.tr.selectLanguage,
                    style: const TextStyle(fontSize: 18)),
                const SizedBox(width: 25),
                CustomLanguageSelectorDropdown(
                  supportedLocales: AppLocalizations.supportedLocales,
                  provider: context.read<ProviderL10n>(),
                  languageChangeHandler: (Locale locale) {
                    // Handle the language change event
                    context
                        .read<SettingsCubit>()
                        .updateLanguage(locale.languageCode);
                    context.go(AppRoutes.home);
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
