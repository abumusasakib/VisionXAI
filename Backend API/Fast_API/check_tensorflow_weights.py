import os
import sys
import platform
import subprocess
import tensorflow as tf

def compute_sha256(file_path):
    system = platform.system()
    try:
        if system == "Windows":
            # Use PowerShell's Get-FileHash
            result = subprocess.run(
                ["powershell", "-Command", f"Get-FileHash -Algorithm SHA256 \"{file_path}\" | Select-Object -ExpandProperty Hash"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        elif system in {"Linux", "Darwin"}:
            # Use openssl on Unix-like systems
            result = subprocess.run(
                ["openssl", "dgst", "-sha256", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split("= ")[1]
        else:
            print(f"Unsupported OS: {system}")
            return None
    except Exception as e:
        print(f"⚠️ Error computing checksum: {e}")
        return None

def check_tensorflow_weights(directory, prefix="imgcap_231005", expected_sha256=None):
    data_file = os.path.join(directory, f"{prefix}.data-00000-of-00001")
    index_file = os.path.join(directory, f"{prefix}.index")
    checkpoint_file = os.path.join(directory, "checkpoint")

    print("📦 Checking TensorFlow checkpoint files...\n")

    # Check that all files exist
    for file in [data_file, index_file, checkpoint_file]:
        if not os.path.exists(file):
            print(f"❌ Missing file: {file}")
            return
    print("✅ All required files are present.")

    # Optional: Check SHA256 hash
    if expected_sha256:
        print("\n🔐 Verifying SHA256 checksum...")
        actual_hash = compute_sha256(data_file)
        if actual_hash:
            print(f"Computed SHA256: {actual_hash}")
            if actual_hash.lower() == expected_sha256.lower():
                print("✅ SHA256 hash matches expected value.")
            else:
                print("❌ SHA256 hash does NOT match the expected value!")
        else:
            print("⚠️ Skipping checksum comparison due to error.")

    # Try loading the checkpoint using TensorFlow
    print("\n🧠 Attempting to load checkpoint with TensorFlow...")
    try:
        ckpt = tf.train.load_checkpoint(directory)
        vars = ckpt.get_variable_to_shape_map()
        print(f"✅ Successfully loaded checkpoint.")
        print(f"Total variables in checkpoint: {len(vars)}")
        for name, shape in list(vars.items())[:10]:  # Show only first 10
            print(f"  - {name}: shape={shape}")
    except Exception as e:
        print(f"❌ Failed to load checkpoint: {e}")

# Example usage
if __name__ == "__main__":
    # Expected hash from known good system
    expected_hash = "33463E9AD1BD74C2B66765773FF69667BB99783693C369FDF16DAB86DC340925"
    model_version = "20250625_042759"
    prefix=f"imgcap_{model_version}"
    check_tensorflow_weights("ImgCap/weights", prefix=prefix, expected_sha256=expected_hash)
