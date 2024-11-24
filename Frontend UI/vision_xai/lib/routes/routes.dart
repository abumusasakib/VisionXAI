import 'package:go_router/go_router.dart';
import 'package:vision_xai/home/home_cubit.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vision_xai/home/home_screen.dart';
import 'package:vision_xai/routes/app_routes.dart';
import 'package:vision_xai/settings/language_settings/language_settings_screen.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/ip_settings/ip_settings_screen.dart';
import 'package:vision_xai/settings/settings_screen.dart';

final GoRouter router = GoRouter(
  initialLocation: AppRoutes.home,
  routes: [
    GoRoute(
      path: AppRoutes.home,
      builder: (context, state) => BlocProvider(
        create: (_) => HomeCubit(),
        child: const Home(),
      ),
    ),
    GoRoute(
      path: AppRoutes.settings,
      builder: (context, state) => BlocProvider(
        create: (context) => SettingsCubit(),
        child: SettingsUI(),
      ),
    ),
    GoRoute(
      path: AppRoutes.ipSettings,
      builder: (context, state) => BlocProvider(
        create: (context) => SettingsCubit(),
        child: IPSettings(),
      ),
    ),
    GoRoute(
      path: AppRoutes.languageSettings,
      builder: (context, state) => BlocProvider(
        create: (context) => SettingsCubit(),
        child: LanguageSettings(),
      ),
    ),
  ],
);
