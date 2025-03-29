import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:vision_xai/home/home_cubit.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/routes/routes.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:arb_utils/state_managers/l10n_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive
  await Hive.initFlutter();

  // Open a box for settings
  await Hive.openBox('settings');

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge,
        overlays: [SystemUiOverlay.top]);

    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle.light.copyWith(
        statusBarBrightness: Brightness.light,
        statusBarIconBrightness: Brightness.dark,
        statusBarColor: Colors.transparent,
        systemNavigationBarColor: const Color(0xFFFEFDFC), // White 2
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
    );

    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => HomeCubit()),
        BlocProvider(create: (context) => SettingsCubit()),
      ],
      child: ChangeNotifierProvider(
        create: (context) => ProviderL10n(),
        child: Builder(
          builder: (context) {
            return MaterialApp.router(
              onGenerateTitle: (cxt) => cxt.tr.appTitle,
              locale: context
                  .watch<ProviderL10n>()
                  .locale, // Dynamically update locale
              localizationsDelegates: const [
                AppLocalizations.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              supportedLocales: AppLocalizations.supportedLocales,
              debugShowCheckedModeBanner: false,
              theme: ThemeData(
                colorScheme: const ColorScheme(
                  brightness: Brightness.light,
                  primary: Color(0xFF089BB7), // Blue Green
                  onPrimary: Colors.black,
                  secondary: Color(0xFF0FC0B8), // Light Sea Green
                  onSecondary: Colors.black,
                  tertiary: Color(0xFFFEFDFC), // White 2
                  onTertiary: Colors.black,
                  surface: Color(0xFFB3D8E1), // Light Blue
                  onSurface: Colors.black,
                  error: Colors.red,
                  onError: Colors.white,
                ),
                useMaterial3: true,
                scaffoldBackgroundColor: const Color(0xFFFEFDFC), // White 2
                appBarTheme: const AppBarTheme(
                  backgroundColor: Color(0xFF089BB7), // Blue Green
                  foregroundColor: Colors.white,
                  elevation: 0,
                ),
                buttonTheme: const ButtonThemeData(
                  buttonColor: Color(0xFF0FC0B8), // Light Sea Green
                  textTheme: ButtonTextTheme.primary,
                ),
                // Ensure black text and icons on buttons
                textButtonTheme: TextButtonThemeData(
                  style: ButtonStyle(
                    foregroundColor: WidgetStateProperty.all(Colors.black),
                  ),
                ),
                elevatedButtonTheme: ElevatedButtonThemeData(
                  style: ButtonStyle(
                    foregroundColor: WidgetStateProperty.all(Colors.black),
                  ),
                ),
                outlinedButtonTheme: OutlinedButtonThemeData(
                  style: ButtonStyle(
                    foregroundColor: WidgetStateProperty.all(Colors.black),
                  ),
                ),
                // Make sure icons are white by default in the primary and secondary contexts
                iconTheme: const IconThemeData(
                  color: Colors.white,
                ),
                primaryIconTheme: const IconThemeData(
                  color: Colors.white,
                ),
              ),
              routerConfig: router,
            );
          },
        ),
      ),
    );
  }
}
