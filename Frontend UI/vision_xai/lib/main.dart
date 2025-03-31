import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:vision_xai/color_palette/palette_state.dart';
import 'package:vision_xai/home/home_cubit.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/routes/routes.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:arb_utils/state_managers/l10n_provider.dart';
import 'package:vision_xai/color_palette/palette_cubit.dart';

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
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.edgeToEdge,
      overlays: [SystemUiOverlay.top],
    );

    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle.light.copyWith(
        statusBarBrightness: Brightness.light,
        statusBarIconBrightness: Brightness.dark,
        statusBarColor: Colors.transparent,
        systemNavigationBarColor: Colors.white,
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
    );

    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => HomeCubit()),
        BlocProvider(create: (context) => SettingsCubit()),
        BlocProvider(
            create: (context) =>
                PaletteCubit()..updateColors()), // Initialize colors
      ],
      child: ChangeNotifierProvider(
        create: (context) => ProviderL10n(),
        child: Builder(
          builder: (context) {
            return BlocBuilder<PaletteCubit, PaletteState>(
              builder: (context, paletteState) {
                return MaterialApp.router(
                  onGenerateTitle: (cxt) => cxt.tr.appTitle,
                  locale: context.watch<ProviderL10n>().locale,
                  localizationsDelegates: const [
                    AppLocalizations.delegate,
                    GlobalMaterialLocalizations.delegate,
                    GlobalWidgetsLocalizations.delegate,
                    GlobalCupertinoLocalizations.delegate,
                  ],
                  supportedLocales: AppLocalizations.supportedLocales,
                  debugShowCheckedModeBanner: false,
                  theme: ThemeData(
                    colorScheme: ColorScheme.light(
                      primary: paletteState.primaryColor,
                      secondary: paletteState.secondaryColor,
                      tertiary: paletteState.backgroundColor,
                    ),
                    scaffoldBackgroundColor: paletteState.backgroundColor,
                    appBarTheme: AppBarTheme(
                      backgroundColor: paletteState.primaryColor,
                      foregroundColor: Colors.white,
                    ),
                    buttonTheme: ButtonThemeData(
                      buttonColor: paletteState.secondaryColor,
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
            );
          },
        ),
      ),
    );
  }
}
