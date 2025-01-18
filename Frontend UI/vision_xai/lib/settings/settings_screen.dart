import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/routes/app_routes.dart';
import 'package:vision_xai/settings/settings_cubit.dart';

class SettingsUI extends StatelessWidget {
  const SettingsUI({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => SettingsCubit(),
      child: Scaffold(
        appBar: AppBar(
          title: Text(context.tr.settingsScreenTitle),
        ),
        body: ListView(
          children: [
            ListTile(
              leading: const Icon(Icons.language),
              title: Text(context.tr.languageSettings),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                context.push(AppRoutes.languageSettings);
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: Text(context.tr.ipConfiguration),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                context.push(AppRoutes.ipSettings);
              },
            ),
          ],
        ),
      ),
    );
  }
}
