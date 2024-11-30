# VisionXAI

A Flutter application with dynamic localization, BLoC state management, Hive for persistence, and routing.

---

## Key Components of this Project

### 1. **Localization Support**

- Localization with `flutter_localizations`.
- ARB files are located in `lib/l10n`.
- Code generation uses `flutter_gen_runner`.

### 2. **State Management**

- Using `flutter_bloc` and `bloc` for managing application state.

### 3. **Persistence**

- Using `hive` and `hive_flutter` for lightweight storage.

### 4. **Dynamic Routing**

- `go_router` for navigation and dynamic route handling.

### 5. **Utilities**

- `intl`: For formatting dates and numbers based on locale.

### 6. **Code Generation Tools**

- `build_runner`: For code generation.
- `flutter_gen_runner`: Automatically generate localization code.

### 7. **Cross-Platform Compatibility**

- **Android**, **Windows**, and **Web** apps can be built and run seamlessly.
- The app is designed to be functional on **mobile**, **desktop**, and **web** platforms.

---

## Directory Structure for VisionXAI

Below is the detailed directory structure for the **VisionXAI** Flutter project. This structure organizes the app into logical modules, ensuring modularity and clarity in code maintenance.

```plaintext
vision_xai/
├── analysis_options.yaml                # Analysis options for linting rules.
├── devtools_options.yaml                # DevTools configuration.
├── l10n.yaml                            # Configuration for Flutter localization.
├── l10n_errors.txt                      # Logs for localization errors.
├── pubspec.yaml                         # Flutter project dependencies and configurations.
├── pubspec.lock                         # Lock file for dependencies.
├── README.md                            # Project documentation.
├── .fvm/                                # Flutter Version Management files.
│   ├── fvm_config.json
│   ├── release
│   └── version
├── .fvmrc                               # FVM version configuration.
├── .gitignore                           # Git ignore rules.
├── .metadata                            # Flutter project metadata.
├── .vscode/                             # Visual Studio Code configurations.
│   ├── launch.json                      # Debugger configurations.
│   └── settings.json                    # Editor-specific settings.
├── android/                             # Android-specific files and configurations.
│   ├── app/
│   │   ├── build.gradle
│   │   └── src/
│   │       ├── main/
│   │       │   ├── AndroidManifest.xml  # Android configuration file.
│   │       │   ├── kotlin/              # Kotlin code for MainActivity.
│   │       │   └── res/                 # Resources for Android app.
│   │           ├── drawable/            # Launch screen resources.
│   │           ├── mipmap-hdpi/         # App launcher icons for different resolutions.
│   │           └── values/              # Style definitions.
│   └── gradle/                          # Gradle wrapper configurations.
├── web/                                 # Web-specific files.
│   ├── index.html                       # HTML entry point for the web app.
│   ├── favicon.png                      # Web favicon.
│   ├── manifest.json                    # Web manifest for PWA features.
│   └── icons/                           # App icons for web.
│       ├── Icon-192.png
│       ├── Icon-512.png
│       ├── Icon-maskable-192.png
│       └── Icon-maskable-512.png
├── windows/                             # Windows-specific files.
│   ├── CMakeLists.txt                   # CMake build configurations.
│   ├── flutter/                         # Flutter-generated Windows integration files.
│   └── runner/                          # App runner configurations for Windows.
├── test/                                # Unit and widget tests.
│   └── widget_test.dart                 # Example widget test.
├── lib/                                 # Main application source code.
│   ├── main.dart                        # Application entry point.
│   ├── constants/                       # Constants for the app.
│   │   └── ipDetails.dart               # IP configuration constants.
│   ├── l10n/                            # Localization files and utilities.
│   │   ├── app_en.arb                   # English language translations.
│   │   ├── app_bn.arb                   # Bengali language translations.
│   │   └── localization_extension.dart  # Localization extension for convenience.
│   ├── routes/                          # Routing configuration.
│   │   ├── app_routes.dart              # Route definitions.
│   │   └── routes.dart                  # GoRouter setup.
│   ├── home/                            # Home screen-related files.
│   │   ├── home_screen.dart             # Home screen UI.
│   │   ├── home_cubit.dart              # State management for home screen.
│   │   └── home_state.dart              # State definitions for home screen.
│   ├── settings/                        # Settings screen and logic.
│   │   ├── ip_settings/                 # IP configuration UI.
│   │   │   └── ip_settings_screen.dart
│   │   ├── language_settings/           # Language selection UI.
│   │   │   └── language_settings_screen.dart
│   │   ├── settings_cubit.dart          # State management for settings.
│   │   ├── settings_screen.dart         # Main settings screen.
│   │   └── settings_state.dart          # State definitions for settings.
│   └── widgets/                         # Shared widgets.
│       └── custom_language_selector_dropdown.dart # Dropdown for language selection.
```

---

### **Key Directories**

- **`lib/`**: Contains all the application logic, widgets, and business logic.
- **`android/`**: Contains Android-specific configurations and resources.
- **`web/`**: Contains web-specific resources, including `index.html`.
- **`windows/`**: Contains Windows-specific build configurations and app runner files.
- **`test/`**: Includes unit and widget tests for validating app functionality.

This directory structure ensures clarity, modularity, and scalability, making it easier for developers to navigate and maintain the **VisionXAI** project.

---

## Setup Instructions

### Install Dependencies

Run the following command to install all project dependencies:

```bash
fvm flutter pub get
```

---

### Generate Localization Files

To generate the Dart localization code from the ARB files, run:

```bash
fvm flutter pub run build_runner build
```

This will generate the `app_localizations.dart` file in the `lib/l10n` directory.

---

## Building and Running the Application

### **Android**

1. Ensure you have the Android SDK installed and configured.
2. Run the following command to build the APK in release mode:

   ```bash
   fvm flutter build apk --release
   ```

3. The generated APK will be located in the `build/app/outputs/flutter-apk/` directory.
4. To build an **AAB** (Android App Bundle) for uploading to the Play Store, use:

   ```bash
   fvm flutter build appbundle --release
   ```

---

### **Windows**

1. Ensure you have the Windows desktop development environment set up, and the `flutter_windows` plugin enabled.
2. Run the following command to build the Windows executable in release mode:

   ```bash
   fvm flutter build windows --release
   ```

3. The executable will be located in the `build/windows/runner/Release/` directory.

To **run** the app on Windows, use:

```bash
fvm flutter run -d windows
```

---

### **Web**

1. **Serve the Application**:
   To serve the app locally for testing, run:

   ```bash
   fvm flutter run -d chrome
   ```

   This will start the app in a web browser on your local machine.

2. **Build for Release**:
   To build the app for deployment on the web, use:

   ```bash
   fvm flutter build web --release
   ```

   The built files will be located in the `build/web/` directory. These files can be deployed to any web server.

---

## Additional Notes

1. **State Management with BLoC**:
   - The app uses **BLoC (Business Logic Component)** for state management in the project. This helps in keeping the UI layer separate from the business logic.
   - Each feature (like Home or Settings) has its own `Cubit` and `State` file to handle specific functionality, making the code modular and easier to maintain.

2. **Localization**:
   - The `l10n/` folder is dedicated to managing the app's language and translations. Each supported language should have an ARB file for storing translated strings.
   - `flutter_localizations` is used to dynamically switch languages based on user preference, and the `flutter_gen_runner` tool is used to generate the Dart localization files automatically.

3. **Persistence (Hive)**:
   - The app uses **Hive** for storing user preferences like IP and port configuration in a lightweight and efficient manner. This is managed inside the `settings/` folder where the user's preferences are saved and loaded.

4. **Routing with `go_router`**:
   - The app uses the **`go_router`** package for navigation and route management. This package is ideal for handling nested routes and providing a declarative approach to routing.
