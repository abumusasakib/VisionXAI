import 'dart:io';
import 'package:bloc/bloc.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart'; // Dio for advanced HTTP requests
import 'package:vision_xai/home/home_state.dart';

class HomeCubit extends Cubit<HomeState> {
  final ImagePicker _picker = ImagePicker();
  final Dio _dio = Dio(); // Initialize Dio for HTTP requests
  CancelToken _cancelToken = CancelToken(); // Token to cancel the request
  bool _isCaptionGenerationInProgress = false; // Track if caption generation is in progress
  bool _shouldStopGeneration = false; // Flag for user stop action

  HomeCubit() : super(HomeState.initial());

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
  Future<void> uploadAndGenerateCaption(String baseUrl) async {
    if (state.imageFile == null) {
      emit(state.copyWith(errorMessage: 'No image selected.'));
      return;
    }

    emit(state.copyWith(isLoading: true, errorMessage: null));

    try {
      // Upload the image first
      await uploadImage(baseUrl);

      // Proceed to caption generation if upload succeeds
      await generateCaption(baseUrl);
    } catch (e) {
      emit(state.copyWith(errorMessage: 'Error during upload or caption generation: $e', isLoading: false));
    }
  }

  /// Uploads the image to the server
  Future<void> uploadImage(String baseUrl) async {
    try {
      final uri = '$baseUrl/upload';
      final formData = FormData.fromMap({
        "image": await MultipartFile.fromFile(
          state.imageFile!.path,
          filename: state.imageFile!.path.split('/').last,
        ),
      });

      final response = await _dio.post(uri, data: formData, cancelToken: _cancelToken);

      if (response.statusCode == 200) {
        emit(state.copyWith(testOutput: 'Image uploaded successfully.'));
      } else {
        throw Exception('Failed to upload image. Status: ${response.statusCode}');
      }
    } catch (e) {
      if (e is DioException && e.type == DioExceptionType.cancel) {
        emit(state.copyWith(errorMessage: 'Image upload was cancelled.'));
      } else {
        throw Exception('An error occurred during image upload: $e');
      }
    }
  }

  /// Requests a caption from the server for the uploaded image
  Future<void> generateCaption(String baseUrl) async {
    if (_isCaptionGenerationInProgress) {
      emit(state.copyWith(testOutput: 'Caption generation already in progress.'));
      return;
    }

    _isCaptionGenerationInProgress = true;
    _shouldStopGeneration = false; // Reset stop flag when starting a new process

    try {
      final uri = '$baseUrl/caption';

      final response = await _dio.get(uri, cancelToken: _cancelToken);

      if (_shouldStopGeneration) {
        emit(state.copyWith(testOutput: 'Caption generation stopped by user.', isLoading: false));
        return;
      }

      if (response.statusCode == 200) {
        final responseData = response.data as Map<String, dynamic>;
        final caption = responseData['caption'] as String;
        emit(state.copyWith(testOutput: caption, isLoading: false));
      } else {
        emit(state.copyWith(
          errorMessage: 'Failed to generate caption. Status: ${response.statusCode}',
          isLoading: false,
        ));
      }
    } catch (e) {
      if (e is DioException && e.type == DioExceptionType.cancel) {
        emit(state.copyWith(errorMessage: 'Caption generation was cancelled.', isLoading: false));
      } else {
        emit(state.copyWith(
          errorMessage: 'An error occurred: $e',
          isLoading: false,
        ));
      }
    } finally {
      _isCaptionGenerationInProgress = false;
      emit(state.copyWith(isLoading: false));
    }
  }

  /// Stops the caption generation process
  void stopCaptionGeneration() {
    if (!_isCaptionGenerationInProgress) {
      emit(state.copyWith(errorMessage: 'No caption generation in progress.'));
      return;
    }

    // Set the flag to stop the process and cancel the request
    _shouldStopGeneration = true;
    _cancelToken.cancel(); // Cancel the ongoing request
    _cancelToken = CancelToken(); // Reinitialize the cancel token for future use
    emit(state.copyWith(
      testOutput: 'Stopping caption generation...',
      isLoading: false,
    ));
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
