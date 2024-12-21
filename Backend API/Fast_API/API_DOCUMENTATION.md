# Image Caption Generation API Documentation

## Overview

The **Image Caption Generation API** allows users to upload an image and generate captions for it in Bengali. It is built using **FastAPI** and utilizes a machine learning model to produce captions.

## Base URL

```text
http://0.0.0.0:5000
```

---

## Endpoints

### 1. Root Endpoint

**Description**: Confirms that the API is live.

**Method**: `GET`

**URL**: `/`

**Response**:

- **Status Code**: `200`
- **Body**:

  ```json
  {
      "message": "Image Caption Generation in Bengali"
  }
  ```

---

### 2. Upload Image

**Description**: Uploads an image for caption generation. This replaces any existing image in the upload folder.

**Method**: `POST`

**URL**: `/upload`

**Request**:

- **File**: `image`
  - **Accepted Formats**: `jpg`, `jpeg`, `png`

**Response**:

- **Status Code**: `200`
- **Body**:

  ```json
  {
      "message": "Image uploaded successfully.",
      "filename": "uploaded_images/image.<extension>"
  }
  ```

**Errors**:

- **Status Code**: `400`
  - If no file is selected:

    ```json
    {
        "detail": "No file selected."
    }
    ```

  - If the file format is invalid:

    ```json
    {
        "detail": "Invalid file format. Only jpg, jpeg, png are supported."
    }
    ```

---

### 3. Generate Caption

**Description**: Generates a caption for the uploaded image.

**Method**: `GET`

**URL**: `/caption`

**Response**:

- **Status Code**: `200`
- **Body**:

  ```json
  {
      "image": "image.<extension>",
      "caption": "<generated_caption>"
  }
  ```

**Errors**:

- **Status Code**: `400`
  - If no image is uploaded:

    ```json
    {
        "detail": "No image found. Please upload an image first."
    }
    ```

- **Status Code**: `500`
  - If caption generation fails:

    ```json
    {
        "detail": "Caption generation failed: <error_message>"
    }
    ```

---

## Configuration Details

### Logging

The API uses **loguru** for logging. Logs are stored in the `logs/app.log` file with the following configuration:

- **Rotation**: Daily
- **Retention**: 7 days
- **Compression**: `zip`

### CORS

CORS middleware is configured to allow requests from any origin. This is useful for development and testing.

---

## Upload Folder

The uploaded images are stored in the `uploaded_images` directory. This folder is cleared each time a new image is uploaded.

---

## Running the API

The API can be run using the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

---

## Error Handling

The API handles errors gracefully with appropriate HTTP status codes and detailed error messages. Logs for errors are stored in the `logs/app.log` file for debugging purposes.

---

## Example Workflow

1. **Check API Status**:
   - Send a `GET` request to `/`.
   - Response:

     ```json
     {
         "message": "Image Caption Generation in Bengali"
     }
     ```

2. **Upload an Image**:
   - Send a `POST` request to `/upload` with an image file.
   - Response:

     ```json
     {
         "message": "Image uploaded successfully.",
         "filename": "uploaded_images/image.<extension>"
     }
     ```

3. **Generate Caption**:
   - Send a `GET` request to `/caption`.
   - Response:

     ```json
     {
         "image": "image.<extension>",
         "caption": "<generated_caption>"
     }
     ```

---

## Notes

- Ensure the ML model and vocabulary files are correctly loaded in the `ImgCap/captioner.py` module.
- Logs are crucial for identifying and debugging issues.

---
