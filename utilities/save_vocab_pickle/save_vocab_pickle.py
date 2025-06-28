import os
import json
import pickle
from datetime import datetime

# 🔹 CONFIGURATION
# Path to the JSON vocabulary file
vocab_json_path = '/results/vocab.json'  # Modify this path if needed

# Generate a unique subdirectory name (e.g., timestamp or model ID)
mdx = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., '20250516_130502'

# Output directory where the pickle file will be saved
output_dir = f'/results/Vocab/{mdx}'
os.makedirs(output_dir, exist_ok=True)

# 🔹 STEP 1: Load vocabulary from JSON
print(f"📖 Loading vocabulary from {vocab_json_path}...")
try:
    with open(vocab_json_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    print(f"✅ Vocabulary loaded with {len(vocab)} tokens.")
except Exception as e:
    print(f"❌ Failed to load JSON vocabulary: {e}")
    exit(1)

# 🔹 STEP 2: Save vocabulary as pickle
pickle_path = os.path.join(output_dir, f'vocab_{mdx}')
try:
    with open(pickle_path, 'wb') as f:
        pickle.dump(vocab, f)
    print(f"✅ Pickle file saved at: {pickle_path}")
except Exception as e:
    print(f"❌ Failed to save pickle file: {e}")
    exit(1)

# 🔍 Optional: Sanity check
try:
    with open(pickle_path, 'rb') as f:
        loaded_vocab = pickle.load(f)
    assert vocab == loaded_vocab
    print("🧪 Sanity check passed: Pickled vocabulary matches original.")
except Exception as e:
    print(f"⚠️ Sanity check failed: {e}")
