# **Image Captioning API**

This project provides an API to generate captions for images using a pre-trained image captioning model. The application is built with FastAPI and supports deployment via Docker. It also includes pyenv setup instructions for easy Python version management.

---

## **Folder Structure**

```text
.
├── .python-version
├── install-pyenv-win.ps1
├── .gitignore
├── .vscode
│   └── launch.json
├── API_DOCUMENTATION.md
├── Dockerfile
├── ImgCap
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-38.pyc
│   │   ├── captioner.cpython-312.pyc
│   │   └── captioner.cpython-38.pyc
│   ├── captioner.py
│   └── weights
│       ├── checkpoint
│       ├── imgcap_231005.data-00000-of-00001
│       ├── imgcap_231005.index
│       ├── readme.txt
│       └── vocab_231005
├── README.md
├── __pycache__
│   ├── main.cpython-312.pyc
│   └── main.cpython-38.pyc
├── docker-compose.yml
├── logs
│   ├── app.2025-03-31_06-16-07_312256.log.zip
│   ├── app.2025-04-08_15-59-08_735091.log.zip
│   └── captioner_2025-04-08_16-03-10_138429.log.zip
├── main.py
├── managed_context
│   └── metadata.json
├── requirements.txt
├── setup.bat
├── setup.ps1
├── setup.sh
└── test_suite_analysis
    └── metadata.json
```

---

## **Setup Instructions**

### **Using Python Locally**

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

1. Run the PowerShell script:

   ```powershell
   .\setup.ps1
   ```

#### **Windows (Command Prompt)**

1. Run the batch script:

   ```cmd
   setup.bat
   ```

---

## **Python Version Management with pyenv**

You can manage Python versions efficiently with **pyenv** (Linux/Mac) or **pyenv-win** (Windows).

### **pyenv (Linux/macOS)**

- Install via automatic installer:

  ```bash
  curl -fsSL https://pyenv.run | bash
  ```

- Or via GitHub clone:

  ```bash
  git clone https://github.com/pyenv/pyenv.git ~/.pyenv
  cd ~/.pyenv && src/configure && make -C src
  ```

### **pyenv-win (Windows)**

- Install via PowerShell:

  ```powershell
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
  ```

- After installation, reopen PowerShell and verify:

  ```powershell
  pyenv --version
  ```

- Useful Commands:

  ```powershell
  pyenv install -l           # List available Python versions
  pyenv install 3.8.5         # Install a specific version
  pyenv global 3.8.5          # Set the global Python version
  pyenv local 3.8.5           # Set project-specific Python version
  pyenv versions              # Show installed versions
  ```

---

## **Testing the API**

### **Swagger UI**

Access Swagger UI at:
`http://localhost:5000/docs`

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

Add the following to `.vscode/launch.json` for debugging with Visual Studio Code:

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

- `ImgCap/weights/`: Pre-trained model weights and vocabulary.
- `main.py`: Entry point for the FastAPI server.
- `logs/`: Compressed application logs.
- `setup.sh`, `setup.ps1`, `setup.bat`: Scripts to automate Docker container deployment.
- `Dockerfile` and `docker-compose.yml`: Docker configuration files.
- `.vscode/launch.json`: VS Code debug configuration.
- `managed_context/`: Context metadata for model usage.

---

## **Additional Resources**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pyenv Documentation](https://github.com/pyenv/pyenv)
- [Pyenv-Win Documentation](https://github.com/pyenv-win/pyenv-win)

---

> **Note**:
> This project is intended for educational and demonstration purposes only, not production-grade deployments.
