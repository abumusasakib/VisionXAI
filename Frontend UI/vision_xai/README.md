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

### `lib/`

This is the main directory for all the Dart code and the business logic of the application. It contains subdirectories and files that correspond to various features and components of the app.

---

### `l10n/`

This directory contains the **localization files** (in ARB format) and is responsible for managing language support in the app. The files here define all the translated strings for different languages.

- **`app_en.arb`**: This ARB (Application Resource Bundle) file contains the English language translations. This file includes key-value pairs for all text displayed in the app in English (e.g., UI labels, buttons, etc.).
  
- **`app_bn.arb`**: This ARB file contains Bengali translations. It mirrors the structure of `app_en.arb` but with translated text for the Bengali language.

**How it works**:

- Each ARB file corresponds to a language, allowing easy localization and translations.
- These files are used by Flutter's localization system to load the appropriate text based on the selected locale.

### `home/`

This directory manages the **Home screen** and its associated logic. It includes all the files related to the UI and state management for the Home screen.

- **`home_screen.dart`**: Contains the main UI code for the home screen of the app. This is where widgets such as images, text, and buttons are defined and laid out for the user.
  
- **`home_cubit.dart`**: This is the BLoC (Business Logic Component) that handles the state for the Home screen. It manages the logic for selecting and uploading images, generating captions, and handling loading states.
  
- **`home_state.dart`**: Contains the state of the `HomeCubit`, which includes properties like the image file, caption text, and loading state. This state is emitted by the `HomeCubit` to update the UI.

**Purpose**:

- The Home directory manages the main content of the app, where the user interacts with image selection, caption generation, and viewing results.

### `settings/`

This directory contains the logic and UI for the **Settings screen**, where the user can modify preferences such as IP address, port, and language.

- **`settings_screen.dart`**: Defines the layout and UI for the settings screen. This file includes widgets for changing the IP configuration, port, and language.
  
- **`settings_cubit.dart`**: Contains the BLoC for managing the state in the settings screen. This includes the logic to load, update, and persist IP and port configuration, as well as handling locale changes.
  
- **`settings_state.dart`**: Holds the state of the settings, including the current IP, port, selected language, and available languages. This is used to update the UI based on the user's choices.

**Purpose**:

- The Settings directory manages all configuration aspects of the app, such as networking (IP/Port settings) and user preferences like language selection.

### `main.dart`

This is the entry point of the Flutter application. It configures the app's root widget, sets up the `MaterialApp`, handles localization delegates, and initializes the `SettingsCubit` for managing app-wide state.

**Purpose**:

- This file ties everything together, initializing the necessary cubits, providers, and the app's locale settings. It ensures that localization and state management are set up before the app UI is displayed.

---

## Setup Instructions

### Setup Flutter Version Manager

Run the following command to setup FVM for Flutter version management:

```bash
fvm install
```

### Installing Dependencies

Run the following command to install all dependencies:

```bash
fvm flutter pub get
```

### Generating Localization Files

Run the following command to generate the localization code:

```bash
fvm flutter pub run build_runner build
```

This will generate the `app_localizations.dart` file in the `lib/l10n` directory.

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

---
