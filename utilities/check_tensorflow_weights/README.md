# 📦 Model Integrity Check

Run this script to verify that the TensorFlow model weights are present, readable, and uncorrupted:

```bash
python check_tensorflow_weights.py
```

Run this command to generate SHA-256 checksums for the model weights:

On Windows:

```powershell
Get-FileHash -Algorithm SHA256 "_Fast_API_Dir_\ImgCap\weights\imgcap__model_version_.data-00000-of-00001"
```

On Linux:

```bash
openssl dgst -sha256 "_Fast_API_Dir_/ImgCap/weights/imgcap__model_version_.data-00000-of-00001"
```
