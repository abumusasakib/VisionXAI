import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:locale_names/locale_names.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  String appVersion = "Loading...";
  String platform = "Unknown";

  @override
  void initState() {
    super.initState();
    _loadAppInfo();
  }

  Future<void> _loadAppInfo() async {
    final packageInfo = await PackageInfo.fromPlatform();

    setState(() {
      appVersion = packageInfo.version;
      try {
        if (kIsWeb) {
          platform = "Web";
        } else if (Platform.isAndroid) {
          platform = "Android";
        } else if (Platform.isIOS) {
          platform = "iOS";
        } else if (Platform.isLinux) {
          platform = "Linux";
        } else if (Platform.isMacOS) {
          platform = "macOS";
        } else if (Platform.isWindows) {
          platform = "Windows";
        } else {
          platform = "Unknown";
        }
      } catch (e) {
        platform = "Unsupported Platform";
      }
    });
  }

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
            if (appVersion != "Loading...")
              Text(
                '${context.tr.version}: $appVersion',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Colors.white,
                ),
              ),
            const SizedBox(height: 5),
            if (platform != "Unknown" && platform != "Unsupported Platform")
              Text(
                '${context.tr.platform}: $platform',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Colors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
