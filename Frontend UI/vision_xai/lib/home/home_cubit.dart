import 'dart:developer';
import 'dart:io';
import 'package:bloc/bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart'; // Dio for advanced HTTP requests
import 'package:vision_xai/home/home_state.dart';
import 'package:vision_xai/l10n/localization_extension.dart';

class HomeCubit extends Cubit<HomeState> {
  final ImagePicker _picker = ImagePicker();
  final Dio _dio = Dio(); // Initialize Dio for HTTP requests
  CancelToken _cancelToken = CancelToken(); // Token to cancel the request
  bool _isCaptionGenerationInProgress =
      false; // Track if caption generation is in progress
  bool _shouldStopGeneration = false; // Flag for user stop action

  final FlutterTts _flutterTts = FlutterTts();

  HomeCubit() : super(HomeState.initial()) {
    _configureTts();
  }

  void _configureTts() async {
    await _flutterTts.awaitSpeakCompletion(true);
    await _flutterTts.setLanguage("bn-BD"); // Bengali (Bangladesh)
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.setVolume(1.0);
    await _flutterTts.setPitch(1.0);

    _flutterTts.setStartHandler(() {
      emit(state.copyWith(isSpeaking: true));
    });

    _flutterTts.setCompletionHandler(() {
      emit(state.copyWith(isSpeaking: false));
    });

    _flutterTts.setCancelHandler(() {
      emit(state.copyWith(isSpeaking: false));
    });

    _flutterTts.setErrorHandler((msg) {
      emit(state.copyWith(isSpeaking: false));
    });

    if (Platform.isIOS) {
      await _flutterTts.setSharedInstance(true);
      await _flutterTts.setIosAudioCategory(
        IosTextToSpeechAudioCategory.ambient,
        [
          IosTextToSpeechAudioCategoryOptions.allowBluetooth,
          IosTextToSpeechAudioCategoryOptions.allowBluetoothA2DP,
          IosTextToSpeechAudioCategoryOptions.mixWithOthers
        ],
        IosTextToSpeechAudioMode.voicePrompt,
      );
    }
  }

  Future<void> speakCaption(String text, BuildContext context) async {
    await _flutterTts.stop(); // Stop any previous speech
    final result = await _flutterTts.speak(text);
    if (result != 1) {
      if (context.mounted) {
        emit(state.copyWith(errorMessage: context.tr.failedToSpeak));
      }
    }
  }

  Future<void> stopSpeaking() async {
    await _flutterTts.stop();
  }

  @override
  Future<void> close() {
    _flutterTts.stop();
    return super.close();
  }

  void setIpAndPort(String ip, String port) {
    emit(state.copyWith(ip: ip, port: port));
  }

  Future<void> selectImage(File file) async {
    emit(state.copyWith(imageFile: file));
  }

  Future<void> pickImage(ImageSource source) async {
    final pickedFile = await _picker.pickImage(source: source);
    if (pickedFile != null) {
      emit(state.copyWith(imageFile: File(pickedFile.path)));
    }
  }

  /// Combined function to handle both upload and caption generation sequentially
  Future<void> uploadAndGenerateCaption(
      String baseUrl, BuildContext context) async {
    if (state.imageFile == null) {
      emit(state.copyWith(errorMessage: context.tr.noImageSelected));
      return;
    }

    _shouldStopGeneration = false; // 🔁 Reset stop flag

    emit(state.copyWith(isLoading: true, errorMessage: null));

    try {
      // Upload the image first
      await uploadImage(baseUrl, context);

      _isCaptionGenerationInProgress = true;

      // Proceed to caption generation if upload succeeds
      if (context.mounted) {
        await generateCaption(baseUrl, context);
      }
    } catch (e, stackTrace) {
      log('Exception in uploadAndGenerateCaption: $e',
          stackTrace: stackTrace, name: 'HomeCubit');
    }
  }

  /// Uploads the image to the server
  Future<void> uploadImage(String baseUrl, BuildContext context) async {
    try {
      final uri = '$baseUrl/upload';
      final formData = FormData.fromMap({
        "image": await MultipartFile.fromFile(
          state.imageFile!.path,
          filename: state.imageFile!.path.split('/').last,
        ),
      });

      final response =
          await _dio.post(uri, data: formData, cancelToken: _cancelToken);

      if (response.statusCode == 200) {
        if (context.mounted) {
          emit(state.copyWith(infoMessage: context.tr.imageUploaded));
        }
      } else {
        if (context.mounted) {
          emit(state.copyWith(
              errorMessage:
                  context.tr.uploadError(response.statusMessage.toString()),
              isLoading: false));
        }
      }
    } catch (e, stackTrace) {
      log('Exception in uploadImage: $e',
          stackTrace: stackTrace, name: 'HomeCubit');
      if (e is DioException && e.type == DioExceptionType.cancel) {
        if (context.mounted) {
          // Handle cancellation specifically
          emit(state.copyWith(errorMessage: context.tr.uploadCancelled));
        }
      } else {
        if (context.mounted) {
          if (e is DioException) {
            emit(state.copyWith(
              errorMessage: _mapDioErrorToMessage(e, context),
              isLoading: false,
            ));
          } else {
            emit(state.copyWith(
              errorMessage: context.tr.unknownError,
              isLoading: false,
            ));
          }
        }
      }
    }
  }

  /// Requests a caption from the server for the uploaded image
  Future<void> generateCaption(String baseUrl, BuildContext context) async {
    _shouldStopGeneration =
        false; // Reset stop flag when starting a new process

    try {
      final uri = '$baseUrl/caption';

      final response = await _dio.get(uri, cancelToken: _cancelToken);

      if (_shouldStopGeneration) {
        if (context.mounted) {
          // If the user requested to stop the caption generation
          _isCaptionGenerationInProgress = false;
          emit(state.copyWith(
              infoMessage: context.tr.captionStopped, isLoading: false));
        }
        return;
      }

      if (response.statusCode == 200) {
        final responseData = response.data as Map<String, dynamic>;
        final caption = responseData['caption'] as String;
        emit(state.copyWith(testOutput: caption, isLoading: false));
      } else {
        if (context.mounted) {
          // Handle non-200 responses
          emit(state.copyWith(
            errorMessage:
                context.tr.captionFailed(response.statusCode.toString()),
            isLoading: false,
          ));
        }
      }
    } catch (e, stackTrace) {
      log('Exception in generateCaption: $e',
          stackTrace: stackTrace, name: 'HomeCubit');
      if (e is DioException && e.type == DioExceptionType.cancel) {
        if (context.mounted) {
          // Handle cancellation specifically
          emit(state.copyWith(
              errorMessage: context.tr.captionGenerationStopped,
              isLoading: false));
        }
      }
    } finally {
      _isCaptionGenerationInProgress = false;
      emit(state.copyWith(isLoading: false));
    }
  }

  /// Stops the caption generation process
  void stopCaptionGeneration(BuildContext context) {
    if (!_isCaptionGenerationInProgress) {
      emit(state.copyWith(errorMessage: context.tr.noCaptionInProgress));
      return;
    }

    // Set the flag to stop the process and cancel the request
    _shouldStopGeneration = true;
    _cancelToken.cancel(); // Cancel the ongoing request
    _cancelToken =
        CancelToken(); // Reinitialize the cancel token for future use
    emit(state.copyWith(
      infoMessage: context.tr.captionStoppedShort,
      isLoading: false,
    ));
  }

  /// Clears the info message from the state
  void clearInfoMessage() {
    emit(state.copyWith(infoMessage: null));
  }

  String _mapDioErrorToMessage(DioException e, BuildContext context) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return context.tr.connectionTimeout;
    }

    if (e.type == DioExceptionType.badResponse) {
      return context.tr.badResponse(e.response?.statusCode?.toString() ?? '');
    }

    if (e.type == DioExceptionType.cancel) {
      return context.tr.requestCancelled;
    }

    if (e.type == DioExceptionType.connectionError ||
        e.error is SocketException) {
      return context.tr.noInternetOrServerUnreachable;
    }
    return context.tr.unknownError;
  }

  /// Resets the state of the HomeCubit
  void reset() {
    _isCaptionGenerationInProgress = false;
    _shouldStopGeneration = false;
    _cancelToken = CancelToken(); // Reset cancel token
    emit(HomeState.initial());
    emit(state.copyWith(errorMessage: null));
  }
}
