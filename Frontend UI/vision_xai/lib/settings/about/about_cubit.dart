import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:vision_xai/settings/about/about_state.dart';

// AboutCubit to manage state
class AboutCubit extends Cubit<AboutState> {
  AboutCubit()
      : super(AboutState(appVersion: "Loading...", platform: "Unknown"));

  Future<void> loadAppInfo() async {
    final packageInfo = await PackageInfo.fromPlatform();
    String platformName = "Unknown";

    try {
      if (kIsWeb) {
        platformName = "Web";
      } else if (Platform.isAndroid) {
        platformName = "Android";
      } else if (Platform.isIOS) {
        platformName = "iOS";
      } else if (Platform.isLinux) {
        platformName = "Linux";
      } else if (Platform.isMacOS) {
        platformName = "macOS";
      } else if (Platform.isWindows) {
        platformName = "Windows";
      }
    } catch (e) {
      platformName = "Unsupported Platform";
    }

    emit(AboutState(
      appVersion: "${packageInfo.version} (${packageInfo.buildNumber})",
      platform: platformName,
    ));
  }
}
