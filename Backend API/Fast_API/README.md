# **Image Captioning API**

## Setup Instructions

Ensure that you have Python 3.10 or higher installed on your system. Recommended to have Python 3.12.4.

1. **Create a Virtual Environment**:

   ```bash
   python -m venv .venv
   ```

2. **Activate the Virtual Environment**:
   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

   - On Windows:

     ```bash
     .venv\Scripts\activate
     ```

3. **Install Requirements**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   uvicorn main:app --reload
   ```

## **Testing the API**

1. **Run the API**:

   ```bash
   uvicorn main:app --reload
   ```

   OR

   ```bash
   python app.py
   ```

2. **Test with Swagger**:
   Visit `http://127.0.0.1:5000/docs` for an interactive Swagger UI.

3. **Test Endpoints**:
   - Use tools like **Postman**, **cURL**, or **Swagger UI** to test the `/upload` and `/caption` endpoints.

4. **Example cURL Commands**:
   - Upload an image:

     ```bash
     curl -X POST "http://127.0.0.1:5000/upload" -F "image=@your_image.jpg"
     ```

   - Generate a caption:

     ```bash
     curl -X GET "http://127.0.0.1:5000/caption"
     ```
