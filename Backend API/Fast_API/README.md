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
   uvicorn main:app --host 0.0.0.0 --port 5000 --reload
   ```

## **Testing the API**

1. **Run the API**:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5000 --reload
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

## **Debugging Configuration**

Add the following configuration to your `.vscode/launch.json` file:

```json
{
    "version": "0.2.0",
    "configurations": [
      {
        "type": "debugpy",
        "request": "launch",
        "name": "Launch FastAPI with Uvicorn",
        "module": "uvicorn",
        "args": [
          "main:app", // Specify the module and app instance
          "--host", "0.0.0.0", // Host to listen on
          "--port", "5000", // Port to use
          "--reload" // Enable auto-reload for development
        ],
        "jinja": true, // Enables Jinja2 template debugging if applicable
        "envFile": "${workspaceFolder}/.env", // Path to the environment variables file
        "console": "integratedTerminal", // Use the integrated terminal for better interaction
        "justMyCode": true // Only debug user code, not external libraries
      }
    ]
  }
```
