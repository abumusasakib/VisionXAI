import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/settings/about/about_cubit.dart';
import 'package:vision_xai/settings/about/about_state.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => AboutCubit()..loadAppInfo(),
      child: const AboutView(),
    );
  }
}

class AboutView extends StatelessWidget {
  const AboutView({super.key});

  @override
  Widget build(BuildContext context) {
    // Define the teal color that matches the logo background
    const Color bgColor = Color(0xFF1A7A85);

    return Scaffold(
      appBar: AppBar(
        title: Text(context.tr.about),
        backgroundColor: bgColor,
        foregroundColor: Colors.white,
      ),
      backgroundColor: bgColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/about.png', width: 500, height: 500),
            const SizedBox(height: 20),
            BlocBuilder<SettingsCubit, SettingsState>(
              builder: (context, state) {
                return Text(
                  '${context.tr.currentLanguage}: ${state.currentLocale.nativeDisplayLanguage}',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                );
              },
            ),
            const SizedBox(height: 10),
            BlocBuilder<AboutCubit, AboutState>(
              builder: (context, state) {
                return Column(
                  children: [
                    if (state.appVersion != "Loading...")
                      Text(
                        '${context.tr.version}: ${state.appVersion}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.white,
                        ),
                      ),
                    const SizedBox(height: 5),
                    if (state.platform != "Unknown" && state.platform != "Unsupported Platform")
                      Text(
                        '${context.tr.platform}: ${state.platform}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.white,
                        ),
                      ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
