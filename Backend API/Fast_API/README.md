# **Image Captioning API**

This project provides an API to generate captions for images using a pre-trained image captioning model. The application is built with FastAPI and supports deployment via Docker.

---

## **Folder Structure**

```text
.
├── ImgCap
│   ├── weights
│   │   ├── checkpoint
│   │   ├── imgcap_231005.data-00000-of-00001
│   │   ├── imgcap_231005.index
│   │   ├── vocab_231005
│   │   └── readme.txt
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-38.pyc
│   │   ├── captioner.cpython-312.pyc
│   │   └── captioner.cpython-38.pyc
│   └── captioner.py
├── setup.bat
├── .gitignore
├── .vscode
│   └── launch.json
├── API_DOCUMENTATION.md
├── Dockerfile
├── README.md
├── __pycache__
│   ├── main.cpython-312.pyc
│   └── main.cpython-38.pyc
├── docker-compose.yml
├── main.py
├── managed_context
│   └── metadata.json
├── requirements.txt
├── setup.ps1
├── setup.sh
└── test_suite_analysis
    └── metadata.json
```

---

## **Setup Instructions**

### **Using Python**

Recommended to have Python 3.8.5 for compatibility with TensorFlow.

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

     ```cmd
     .venv\Scripts\activate
     ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python main.py
   ```

---

### **Using Docker**

#### **Linux/macOS**

1. Ensure `setup.sh` is executable:

   ```bash
   chmod +x setup.sh
   ```

2. Run the setup script:

   ```bash
   ./setup.sh
   ```

#### **Windows (PowerShell)**

1. Execute the PowerShell script:

   ```powershell
   .\setup.ps1
   ```

#### **Windows (Command Prompt)**

1. Run the batch script:

   ```cmd
   setup.bat
   ```

---

## **Testing the API**

### **Swagger UI**

Access the Swagger UI at `http://localhost:5000/docs` for an interactive interface to test the API endpoints.

### **Example cURL Commands**

- **Upload an Image**:

  ```bash
  curl -X POST "http://127.0.0.1:5000/upload" -F "image=@path_to_image.jpg"
  ```

- **Generate a Caption**:

  ```bash
  curl -X GET "http://127.0.0.1:5000/caption"
  ```

---

## **Debugging Configuration**

Add the following to `.vscode/launch.json` for debugging in Visual Studio Code:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Run FastAPI",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "justMyCode": true,
      "env": {
        "PYTHONUNBUFFERED": "1"  // Ensure logs are flushed immediately
      },
      "args": [],
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Debug FastAPI",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "justMyCode": false, // Include third-party libraries in debugging
      "args": [],
      "env": {
        "PYTHONUNBUFFERED": "1"
      },
    }
  ]
}

```

---

## **Folder Details**

### **Key Folders and Files**

- `ImgCap/weights/`: Contains the pre-trained model weights and vocabulary files.
- `main.py`: The entry point for the FastAPI application.
- `setup.sh`, `setup.ps1`, `setup.bat`: Platform-specific setup scripts for Docker.
- `Dockerfile`: Defines the Docker image setup.
- `docker-compose.yml`: Manages containerized deployment.
- `requirements.txt`: Lists Python dependencies.
- `.vscode/launch.json`: Configuration for debugging with Visual Studio Code.

---

## **Additional Resources**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.starlette.io/uvicorn/)

---

**Note**: This project is intended for educational and demonstration purposes only. It is not intended for production use.
