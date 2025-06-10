# Define the FLUTTER_VERSION argument with a default fallback
ARG FLUTTER_VERSION=3.22.3

# Use the specified Flutter version as the base image
FROM ghcr.io/cirruslabs/flutter:3.22.1

RUN echo "Using Flutter version $FLUTTER_VERSION"

# Default fallback for the the package name
ARG PACKAGE_NAME=my_flutter_app

# Set environment variable for PACKAGE_NAME for later use
ENV PACKAGE_NAME=vision_xai

RUN echo "Using Package name $PACKAGE_NAME"

# Running flutter doctor to ensure all dependencies are installed correctly
RUN flutter doctor -v

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Set up FVM
# # Install FVM
# RUN curl -fsSL https://fvm.app/install.sh | bash

# # Install FVM globally
# RUN dart pub global activate fvm

# # Install specified Flutter version for project
# RUN fvm install

# Get Flutter packages
# RUN fvm flutter pub get

# Generate localization files
# RUN fvm flutter gen-l10n

# Run the build_runner
# RUN fvm flutter pub run build_runner build

# Build the Flutter app
# Build for Android or iOS
# For Android:
# RUN fvm flutter build apk --release
# For iOS:
# RUN flutter build ios --release

# Build the Flutter app for web
# RUN fvm flutter build web --release

# Get Flutter packages
RUN flutter pub get

# Generate localization files
RUN flutter gen-l10n

# Run the build_runner to generate code
RUN flutter pub run build_runner build --delete-conflicting-outputs

# Build the Flutter app for Android (APK)
# For Android:
RUN flutter build apk --release && \
    mkdir -p /output && \
    mv build/app/outputs/flutter-apk/app-release.apk /output/${PACKAGE_NAME}-release.apk

RUN echo "The APK will be available in /build/${PACKAGE_NAME}-release.apk"

# Build the Flutter app for web
RUN flutter build web --release

# Install a simple web server to serve the Flutter web build
RUN apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
RUN npm install -g serve

# Expose the build output directory and the web server port, and start server
VOLUME /app/build
EXPOSE 5000

# Output build information
RUN echo "The Flutter web app will be hosted at http://localhost:5000"
RUN echo "Press Ctrl+C twice to quit"

# Serve the web app using a simple web server
CMD ["serve", "-s", "/app/build/web", "-l", "5000"]