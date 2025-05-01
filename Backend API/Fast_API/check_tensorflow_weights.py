import os
import tensorflow as tf

def check_tensorflow_weights(directory, prefix="imgcap_231005"):
    data_file = os.path.join(directory, f"{prefix}.data-00000-of-00001")
    index_file = os.path.join(directory, f"{prefix}.index")
    checkpoint_file = os.path.join(directory, "checkpoint")

    print("Checking TensorFlow checkpoint files...\n")

    # Check that all files exist
    if not os.path.exists(data_file):
        print(f"❌ Data file missing: {data_file}")
        return
    if not os.path.exists(index_file):
        print(f"❌ Index file missing: {index_file}")
        return
    if not os.path.exists(checkpoint_file):
        print(f"❌ Checkpoint file missing: {checkpoint_file}")
        return

    print("✅ All required files are present.")

    # Try loading the checkpoint using TensorFlow
    try:
        ckpt = tf.train.load_checkpoint(directory)
        vars = ckpt.get_variable_to_shape_map()
        print(f"\n✅ Successfully loaded checkpoint.")
        print(f"Total variables in checkpoint: {len(vars)}")
        for name, shape in list(vars.items())[:10]:  # Show only the first 10 for brevity
            print(f"  - {name}: shape={shape}")
    except Exception as e:
        print(f"\n❌ Failed to load checkpoint: {e}")

# Example usage
if __name__ == "__main__":
    check_tensorflow_weights("ImgCap/weights")
