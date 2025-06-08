import 'dart:io';

import 'package:vision_xai/constants/ip_details.dart';

class HomeState {
  final String ip;
  final String port;
  final File? imageFile;
  final bool isLoading;
  final bool isFetching;
  final bool isSpeaking;
  final String testOutput;
  final String? errorMessage; // Nullable error message
  final String? infoMessage; // Nullable info message

  HomeState({
    required this.ip,
    required this.port,
    this.imageFile,
    required this.isLoading,
    required this.isFetching,
    required this.isSpeaking,
    required this.testOutput,
    this.errorMessage,
    this.infoMessage,
  });

  factory HomeState.initial() => HomeState(
        ip: IPDetails.defaultIP,
        port: IPDetails.defaultPort,
        imageFile: null,
        isLoading: false,
        isFetching: false,
        isSpeaking: false,
        testOutput: '',
        errorMessage: null,
        infoMessage: null,
      );

  HomeState copyWith({
    String? ip,
    String? port,
    File? imageFile,
    bool? isLoading,
    bool? isFetching,
    bool? isSpeaking,
    String? testOutput,
    String? errorMessage,
    String? infoMessage,
  }) {
    return HomeState(
      ip: ip ?? this.ip,
      port: port ?? this.port,
      imageFile: imageFile ?? this.imageFile,
      isLoading: isLoading ?? this.isLoading,
      isFetching: isFetching ?? this.isFetching,
      isSpeaking: isSpeaking ?? this.isSpeaking,
      testOutput: testOutput ?? this.testOutput,
      errorMessage: errorMessage,
      infoMessage: infoMessage,
    );
  }
}