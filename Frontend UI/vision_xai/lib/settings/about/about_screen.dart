import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Define the teal color that matches the logo background
    const Color bgColor = Color(0xFF1A7A85);

    return Scaffold(
      // Set the app bar background color
      appBar: AppBar(
        title: Text(context.tr.about),
        backgroundColor: bgColor,
        // For proper contrast with teal background
        foregroundColor: Colors.white,
      ),
      // Set the entire screen background color
      backgroundColor: bgColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/about.png'),
            const SizedBox(height: 20),
            BlocBuilder<SettingsCubit, SettingsState>(
              builder: (context, state) {
                return Text(
                  '${context.tr.currentLanguage}: ${state.currentLocale.nativeDisplayLanguage}',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors
                        .white, // For better readability on teal background
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
