import 'dart:io';

import 'package:vision_xai/constants/ipDetails.dart';

class HomeState {
  final String ip;
  final String port;
  final File? imageFile;
  final bool isLoading;
  final bool isFetching;
  final String testOutput;
  final String? errorMessage; // Nullable error message

  HomeState({
    required this.ip,
    required this.port,
    this.imageFile,
    required this.isLoading,
    required this.isFetching,
    required this.testOutput,
    this.errorMessage,
  });

  factory HomeState.initial() => HomeState(
        ip: IPDetails.defaultIP,
        port: IPDetails.defaultPort,
        imageFile: null,
        isLoading: false,
        isFetching: false,
        testOutput: '',
        errorMessage: null,
      );

  HomeState copyWith({
    String? ip,
    String? port,
    File? imageFile,
    bool? isLoading,
    bool? isFetching,
    String? testOutput,
    String? errorMessage,
  }) {
    return HomeState(
      ip: ip ?? this.ip,
      port: port ?? this.port,
      imageFile: imageFile ?? this.imageFile,
      isLoading: isLoading ?? this.isLoading,
      isFetching: isFetching ?? this.isFetching,
      testOutput: testOutput ?? this.testOutput,
      errorMessage: errorMessage,
    );
  }
}