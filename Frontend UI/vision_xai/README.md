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

- **Android** and **Windows** apps can be built and run seamlessly.
- The app is designed to be functional on both **mobile** and **desktop** platforms.

---

## Directory Structure

The directory structure of the **VisionXAI** Flutter project is organized to maintain clear separation between the different modules and functionalities, such as localization, state management, UI components, and persistence. Here's a breakdown of the project structure:

```text
lib/
├── l10n/
│   ├── app_en.arb
│   ├── app_bn.arb
├── home/
│   ├── home_screen.dart
│   ├── home_cubit.dart
│   └── home_state.dart
├── settings/
│   ├── settings_screen.dart
│   ├── settings_cubit.dart
│   └── settings_state.dart
├── main.dart
```

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

## Building the Application for Different Platforms

The **VisionXAI** app can be built for **Android** and **Windows** in release mode. Below are the instructions for each platform.

### **Building for Android**

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

### **Building for Windows**

1. Ensure you have the Windows desktop development environment set up, and the `flutter_windows` plugin enabled.
2. Run the following command to build the Windows executable in release mode:

   ```bash
   fvm flutter build windows --release
   ```

3. The executable will be located in the `build/windows/runner/Release/` directory.

---

## Running the Application on Windows

### Prerequisites:

- Install and set up Flutter's desktop support for Windows.
- Use the following command to run the app on Windows:

```bash
fvm flutter run -d windows
```

This will launch the app in debug mode, allowing you to test and interact with the Windows application directly.

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
