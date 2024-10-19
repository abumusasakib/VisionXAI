# VisionXAI: Image Caption Generation in Bengali with Explainable AI (xAI)

VisionXAI is a mobile application project designed to generate detailed image captions in Bengali. It integrates Explainable AI (xAI) to provide insights into how the AI model generates captions, fostering trust and understanding. This project is aimed at increasing accessibility for Bengali-speaking users and visually impaired individuals by offering rich image descriptions in their native language.

## Features

- **Image Caption Generation**: Captions images in Bengali by using pre-trained AI models.
- **Explainable AI (xAI)**: Provides an explainability layer that highlights important features in the image and explains how the captions were generated.
- **Mobile Application**: Cross-platform app built using Flutter.
- **Flask API**: A backend API for handling image uploads and caption generation.
- **Local Execution**: The backend API runs locally and processes images to return Bengali captions.

## Project Components

### 1. Mobile Application (Frontend)

- Developed using **Flutter** for cross-platform compatibility (iOS and Android).
- Integrates with the Flask API to upload images and retrieve Bengali captions.
- Provides a user-friendly interface fully localized in Bengali.

### 2. Backend API (Flask)

- API developed using **FastAPI** to handle image uploads and process caption generation.
- Integrates the pre-trained Bengali image captioning model.
- Runs locally and returns generated captions in Bengali.

### 3. Model

This project involves training a multimodal Transformer model for image captioning.

1. Dataset:
   - The dataset is a collection of 9,154 images paired with two captions in Bengali.
   - The dataset consists of images paired with two captions each.
   - It's split into an 80% training set (7,323 samples) and a 20% test set (1,831 samples).
   - Image augmentation is applied to increase data diversity.
   - Captions are vectorized.
   - The data is prepared using TensorFlow Dataset API.

2. Model Architecture:
   - The model is a Transformer-based architecture designed for image-to-text tasks.
   - It uses EfficientNetB0 as the CNN backbone for image feature extraction.
   - Custom Encoder and Decoder blocks are implemented by inheriting from TensorFlow's Layer class.
   - A Positional Embedding layer is included.
   - The final model is created by compiling these layers and inheriting from TensorFlow's Model class.

3. Training Process:
   - A custom loss function is defined.
   - Early stopping is implemented to prevent overfitting.
   - The model is compiled with the defined loss function and other unspecified parameters.
   - The training process checks for previously saved weights and loads them if available.

4. Text Generation:
   - A lookup dictionary is created.
   - An output sequence length is set, determining the maximum length of generated captions.

This model is designed for generating textual captions given input images, utilizing a state-of-the-art Transformer architecture combined with a pre-trained CNN for image feature extraction.

## Technology Stack

- **Flutter**: For frontend mobile app development.
- **FastAPI**: For backend API development.
- **Grad-CAM**, **LIME**: For Explainable AI integration.
- **Python 3.8.10**: For running the backend Flask API.

## Prerequisites

### Backend API Setup

Before running the Flask API, ensure the following are installed:

1. **Python 3.8.10 or above**: Check version compatibility.

2. **Required Dependencies**: Install the necessary Python packages.

   ```bash
   pip install -r requirements.txt
   ```

3. **Model Weights**: Ensure the pre-trained model weights are downloaded and saved in the `ImgCap` package. Without the weights, the API will not function.

### Running the Flask API

1. Start the API by running the `main.py` script in the project directory (Flask_API).

   ```bash
   python main.py
   ```

2. After executing, the server will display an IP address in the console. Use this IP to communicate with the API from the Flutter app.

3. **Update IP in App**: Make sure to update the IP address in the mobile app's configuration with the one shown after running the Flask server.

## Image Captioning Model

- **Dataset**: The model is trained on a dataset of **9,154 images** paired with captions in Bengali, sourced from [this dataset](https://data.mendeley.com/datasets/rxxch9vw59/2).

## Local Development Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the project directory**:

   ```bash
   cd VisionXAI
   ```

3. **Install the backend dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask API**:

   ```bash
   python main.py
   ```

5. **Run the Flutter app**:

   ```bash
   flutter run
   ```

   Open the Flutter project (vision_xai) in your preferred IDE (VSCode, Android Studio) and run the app on an Android/iOS device.

## Notes

- **Local Execution**: The Flask API is designed for local use, and the IP address shown in the console is dynamic. Make sure to update the IP address in the mobile app whenever the Flask server is restarted.
- **Model Weights**: Ensure the correct model weights are placed in the `ImgCap` package as they are crucial for generating accurate captions.
- **Explainable AI**: The xAI features (using Grad-CAM or LIME) allow users to understand why specific parts of the image were selected for captioning.
