# **Image Captioning API**

This project provides an API to generate captions for images using a pre-trained image captioning model. The application is built with **FastAPI** and supports deployment via **Docker**, including **pyenv** support for Python version management and weight transfer support via PowerShell.

---

## **Folder Structure**

```text
.
├── .env                     # Your environment variables (excluded from Git)
├── .gitignore
├── .python-version          # Managed by pyenv/pyenv-win
├── .vscode/
│   └── launch.json
├── API_DOCUMENTATION.md
├── Dockerfile
├── ImgCap/
│   ├── __init__.py
│   ├── captioner.py
│   └── weights/
│       ├── checkpoint
│       ├── imgcap_231005.data-00000-of-00001
│       ├── imgcap_231005.index
│       ├── readme.txt
│       └── vocab_231005
├── README.md
├── check_tensorflow_weights.py     # Script to verify model file integrity
├── docker-compose.yml
├── install-pyenv-win.ps1
├── logs/
│   └── *.log.zip
├── main.py
├── managed_context/
│   └── metadata.json
├── requirements.txt
├── setup.bat / setup.sh / setup.ps1
├── test_suite_analysis/
│   └── metadata.json
├── transfer_weight_files.ps1       # PowerShell script for remote model file sync
└── .env.example              # Template for your .env file
```

---

## ⚙️ Setup Instructions

### ▶️ Using Python Locally

Recommended Python version: **3.8.5**

1. **Create a Virtual Environment**:

   ```bash
   python -m venv .venv
   ```

2. **Activate the Virtual Environment**:

   * On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

   * On Windows:

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

### 🐳 Using Docker

#### On Linux/macOS

```bash
chmod +x setup.sh
./setup.sh
```

#### On Windows

* PowerShell:

  ```powershell
  .\setup.ps1
  ```

* Command Prompt:

  ```cmd
  setup.bat
  ```

---

## 🐍 Python Version Management with pyenv

You can use `pyenv` (Linux/macOS) or `pyenv-win` (Windows) to lock Python to version 3.8.5.

### Linux/macOS

```bash
curl -fsSL https://pyenv.run | bash
```

Or manually:

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cd ~/.pyenv && src/configure && make -C src
```

### Windows (pyenv-win)

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Then verify and install:

```powershell
pyenv --version
pyenv install 3.8.5
pyenv global 3.8.5
```

---

## 🔁 Sync Weights from Local Machine

Use `transfer_weight_files.ps1` for syncing model weights via `scp` over SSH:

> Copy `.env.example` to `.env` and fill in your actual values.

Example `.env.example`:

```dotenv
LOCAL_PATH=D:/your/local/path/to/weights
REMOTE_USER=root
REMOTE_HOST=192.168.0.101
REMOTE_PATH=/mnt/dietpi_userdata/visionxai/
```

Then run:

```powershell
.\transfer_weight_files.ps1
```

---

## 🧪 Testing the API

* Swagger UI:
  `http://localhost:5000/docs`

* Example cURL:

  ```bash
  curl -X POST "http://127.0.0.1:5000/upload" -F "image=@path_to_image.jpg"
  curl -X GET "http://127.0.0.1:5000/caption"
  ```

---

## 🐞 Debugging with VS Code

`.vscode/launch.json` contains configurations for:

* Run with FastAPI
* Debug with FastAPI

Both set `PYTHONUNBUFFERED=1` for clean logs.

---

## 📦 Model Integrity Check

Run this script to verify that your TensorFlow model weights are present, readable, and uncorrupted:

```bash
python check_tensorflow_weights.py
```

---

## 📚 Resources

* [FastAPI Docs](https://fastapi.tiangolo.com/)
* [Uvicorn Docs](https://www.uvicorn.org/)
* [Pyenv](https://github.com/pyenv/pyenv)
* [Pyenv-Win](https://github.com/pyenv-win/pyenv-win)

---

> **Note**: This project is for educational/demo purposes. Production deployments may require additional security and performance hardening.
