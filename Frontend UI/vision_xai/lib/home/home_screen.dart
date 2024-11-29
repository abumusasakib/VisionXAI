import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:vision_xai/constants/ipDetails.dart';
import 'dart:io';

import 'package:vision_xai/home/home_cubit.dart';
import 'package:vision_xai/home/home_state.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/routes/app_routes.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart';

Future<String> _getBaseUrl() async {
  var box = await Hive.box('settings');

  // Default values
  final defaultIp = IPDetails.defaultIP;
  final defaultPort = IPDetails.defaultPort;

  // Get IP and Port from Hive, fallback to defaults if not set
  final ip = box.get("ip", defaultValue: defaultIp);
  final port = box.get("port", defaultValue: defaultPort);

  return 'http://$ip:$port';
}

class Home extends StatelessWidget {
  const Home({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.tr.appTitle),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: () {
              // Navigate to the settings page
              context.push(AppRoutes.settings);
            },
            icon: const Icon(Icons.settings),
          ),
        ],
      ),
      body: BlocListener<SettingsCubit, SettingsState>(
        listener: (context, state) {
          debugPrint(
              'BlocListener detected state change: ${state.currentLocale.languageCode}');
        },
        child: BlocListener<HomeCubit, HomeState>(
          listener: (context, state) {
            if (state.errorMessage != null) {
              // Show error dialog
              showDialog(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: Text(context.tr.errorTitle),
                    content: Text(state.errorMessage!),
                    actions: [
                      TextButton(
                        onPressed: () {
                          context.read<HomeCubit>().reset();
                          Navigator.of(context).pop();
                        },
                        child: Text(context.tr.ok),
                      ),
                    ],
                  );
                },
              );
            }
          },
          child: BlocBuilder<HomeCubit, HomeState>(
            builder: (context, state) {
              final cubit = context.read<HomeCubit>();
              final picker = ImagePicker();

              return LayoutBuilder(
                builder: (context, constraints) {
                  final isWideScreen = constraints.maxWidth > 600;

                  return SafeArea(
                    child: SingleChildScrollView(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: isWideScreen
                            ? Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    flex: 3,
                                    child: _buildImageDisplay(context, state),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    flex: 2,
                                    child: _buildControls(
                                        context, cubit, state, picker),
                                  ),
                                ],
                              )
                            : Column(
                                mainAxisSize: MainAxisSize
                                    .min, // Ensuring Column doesn't expand indefinitely
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  _buildImageDisplay(context, state),
                                  const SizedBox(height: 16),
                                  _buildControls(context, cubit, state, picker),
                                ],
                              ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildImageDisplay(BuildContext context, HomeState state) {
    // Image or Placeholder
    return state.imageFile != null
        ? Image.file(
            File(state.imageFile!.path),
            height: 200,
            fit: BoxFit.cover,
          )
        : Container(
            height: 200, // Providing a fixed height for this widget
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(context.tr.noImageSelected),
            ),
          );
  }

  Widget _buildControls(BuildContext context, HomeCubit cubit, HomeState state,
      ImagePicker picker) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Button to Select Image
        ElevatedButton.icon(
          onPressed: () async {
            final pickedImage = await picker.pickImage(
              source: ImageSource.gallery,
            );
            if (pickedImage != null) {
              cubit.selectImage(File(pickedImage.path));
            }
          },
          icon: const Icon(Icons.photo_library),
          label: Text(context.tr.selectImageFromGallery),
        ),
        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: () async {
            final pickedImage = await picker.pickImage(
              source: ImageSource.camera,
            );
            if (pickedImage != null) {
              cubit.selectImage(File(pickedImage.path));
            }
          },
          icon: const Icon(Icons.camera_alt),
          label: Text(context.tr.camera),
        ),
        const SizedBox(height: 16),
        // Button to Upload Image
        ElevatedButton.icon(
          onPressed: state.isLoading
              ? null
              : () async {
                  final baseUrl = await _getBaseUrl();
                  cubit.startCaptionGeneration(
                      '$baseUrl/upload'); // The `/upload` is the endpoint
                },
          icon: const Icon(Icons.cloud_upload),
          label: state.isLoading
              ? const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                )
              : Text(context.tr.generateCaption),
        ),
        const SizedBox(height: 16),
        if (state.isLoading)
          ElevatedButton.icon(
            onPressed: () {
              cubit.stopCaptionGeneration();
            },
            icon: const Icon(Icons.stop),
            label: const Text('Stop'),
          ),
        const SizedBox(height: 16),
        if (state.isLoading)
          Center(
            child: Text(
              context.tr.generatingCaption,
              style: TextStyle(fontSize: 16, fontStyle: FontStyle.italic),
            ),
          ),
        const SizedBox(height: 16),
        // Text Output for Caption
        Container(
          constraints: const BoxConstraints(
              minHeight: 100), // Ensuring it has a minimum height
          child: Center(
            child: state.testOutput.isNotEmpty
                ? Text(
                    state.testOutput,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 18),
                  )
                : Text(
                    context.tr.captionText,
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
          ),
        ),
      ],
    );
  }
}
