import os
import re
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import TextVectorization
from tensorflow.keras.applications import efficientnet
from loguru import logger

# Desired image dimensions
IMAGE_SIZE = (224, 224)

# Vocabulary size
VOCAB_SIZE = 6000

# Fixed length allowed for any sequence
SEQ_LENGTH = 8

# Dimension for the image embeddings and token embeddings
EMBED_DIM = 256

# Per-layer units in the feed-forward network
FF_DIM = 128

# Model Version
mdx = "20250714_141134"

# Directory Path
WEIGHTS_DIR = "ImgCap/weights/"
VOCAB_FILE = f"{WEIGHTS_DIR}vocab_{mdx}"

# Setup loguru logger
logger.add(
    "logs/captioner_{time}.log",
    rotation="1 day",  # Rotate log every day
    retention="7 days",  # Keep logs for the last 7 days
    compression="zip",  # Compress old log files
    level="INFO",  # Default log level
)
# Suppress repetitive TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Show only errors and critical warnings


# Load Vocabulary
def load_vocab(filepath):
    try:
        logger.info(f"Loading vocabulary from {filepath}")
        with open(filepath, "rb") as f:
            vocab = pickle.load(f)
        logger.info("Vocabulary loaded successfully")

        # Update the vocabulary size
        global VOCAB_SIZE
        VOCAB_SIZE = len(vocab)

        return vocab
    except Exception as e:
        logger.error(f"Error loading vocabulary file: {e}")
        return None


vocab = load_vocab(VOCAB_FILE)


# Custom standardization
def custom_standardization(input_string):
    lowercase = tf.strings.lower(input_string)
    return tf.strings.regex_replace(lowercase, "[%s]" % re.escape(strip_chars), "")


# Using raw string for strip_chars
strip_chars = r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
strip_chars = strip_chars.replace("<", "").replace(">", "")

# Initialize TextVectorization
try:
    if vocab:
        vectorization = TextVectorization(
            max_tokens=VOCAB_SIZE,
            output_mode="int",
            output_sequence_length=SEQ_LENGTH,
            standardize=custom_standardization,
            vocabulary=vocab,
        )
    else:
        logger.error("Vocabulary is not defined.")
        raise ValueError("Vocabulary is not defined.")
except Exception as e:
    logger.error(f"Error initializing TextVectorization: {e}")
    vectorization = None

# Data augmentation for image data
image_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),  # Reduced rotation for faster preprocessing
        layers.RandomContrast(0.2),  # Lighter contrast adjustment
        # layers.RandomTranslation(0.1, 0.1),
    ]
)


# Decode, resize, and preprocess images
def decode_and_resize(img_path):
    try:
        img = tf.io.read_file(img_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMAGE_SIZE)
        img = tf.image.convert_image_dtype(img, tf.float32)
        return img
    except Exception as e:
        logger.error(f"❌ Error in decoding and resizing image {img_path}: {e}")


# Defining the Model
# CNN
def get_cnn_model():
    try:
        base_model = efficientnet.EfficientNetB4(
            input_shape=(*IMAGE_SIZE, 3),
            include_top=False,
            weights="imagenet",
        )
        # We freeze our feature extractor
        base_model.trainable = False
        base_model_out = base_model.output

        # Reduce the sequence length using a pooling operation
        # Using GlobalAveragePooling2D to reduce the spatial dimensions
        base_model_out = layers.GlobalAveragePooling2D()(base_model_out)

        # Project the output to match the embedding size
        # Increase embedding projection for richer features
        base_model_out = layers.Dense(EMBED_DIM, activation="relu")(base_model_out)
        base_model_out = layers.Dense(EMBED_DIM, dtype="float32")(base_model_out)

        cnn_model = keras.models.Model(base_model.input, base_model_out)

        # Print CNN Model Summary
        logger.info("CNN Model Loaded")
        # print("\nCNN Model Summary:")
        # cnn_model.summary()

        return cnn_model
    except Exception as e:
        logger.error(f"Error loading CNN model: {e}")


# Positional Encoding and Encoder/Decoder


# Encoder
class TransformerEncoderBlock(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads=4, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads

        # Multi-Head Self-Attention with 4 heads (was 1)
        self.attention_1 = layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=embed_dim,
            dropout=dropout_rate,  # previously 0.1
        )

        # Layer normalizations
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()

        # Feed-forward layer with increased dense_dim
        self.dense_1 = layers.Dense(embed_dim, activation="relu")
        self.dense_2 = layers.Dense(embed_dim)

        # Dropout for better generalization
        self.dropout_1 = layers.Dropout(dropout_rate)

    def call(self, inputs, training, mask=None):
        inputs = tf.cast(inputs, dtype=tf.float32)  # Ensure correct dtype

        # Input shape
        # logger.debug(f"Encoder Input Shape: {inputs.shape}")

        # logger.debug(f"Encoder Input Shape before LayerNorm: {inputs.shape}")
        # Apply LayerNorm before attention
        inputs = self.layernorm_1(inputs)
        # logger.debug(f"Encoder Input Shape after LayerNorm: {inputs.shape}")

        # inputs = self.dense_1(inputs)

        # Self-attention layer
        attention_output_1 = self.attention_1(
            query=inputs,
            value=inputs,
            key=inputs,
            # attention_mask=None,  # No need for masking padded tokens
            training=training,
        )

        # Residual connection and normalization
        out_1 = self.layernorm_2(inputs + attention_output_1)

        # Feed-forward network
        out_2 = self.dense_1(out_1)
        out_2 = self.dropout_1(out_2, training=training)
        out_2 = self.dense_2(out_2)

        # Output shape
        # logger.debug(f"Encoder Output Shape: {out_1.shape}")
        return out_1 + out_2  # Residual connection for stability


# Positional Encoding
class PositionalEmbedding(layers.Layer):
    def __init__(self, sequence_length, vocab_size, embed_dim, **kwargs):
        super().__init__(**kwargs)
        self.token_embeddings = layers.Embedding(
            input_dim=vocab_size, output_dim=embed_dim
        )
        self.position_embeddings = layers.Embedding(
            input_dim=sequence_length, output_dim=embed_dim
        )
        self.sequence_length = sequence_length
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.embed_scale = tf.math.sqrt(tf.cast(embed_dim, tf.float32))

    def call(self, inputs):
        # logger.debug(f"Positional Embedding Input Shape: {inputs.shape}")

        # Get input shape and positions
        length = tf.shape(inputs)[-1]
        positions = tf.range(start=0, limit=length, delta=1)

        # Embed tokens and positions
        embedded_tokens = self.token_embeddings(inputs)
        embedded_tokens = embedded_tokens * self.embed_scale  # Apply scaling
        embedded_positions = self.position_embeddings(positions)

        # Embeddings shape
        # logger.debug(f"Positional Embedding Output Shape: {embedded_tokens.shape}")
        # logger.debug(f"embedded_tokens dtype: {embedded_tokens.dtype}")
        # logger.debug(f"embedded_positions dtype: {embedded_positions.dtype}")

        # Return combined embeddings
        return embedded_tokens + embedded_positions

    def compute_mask(self, inputs, mask=None):
        return tf.math.not_equal(inputs, 0)


# Decoder
class TransformerDecoderBlock(layers.Layer):
    def __init__(self, embed_dim, ff_dim=1024, num_heads=4, dropout_rate=0.3, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.ff_dim = ff_dim
        self.num_heads = num_heads

        # Attention layers
        # Self-attention layer
        self.attention_1 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim, dropout=dropout_rate
        )

        # Cross-attention layer (image-text)
        self.attention_2 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim, dropout=dropout_rate
        )

        # Feed-forward layers (larger)
        self.ffn_layer_1 = layers.Dense(ff_dim, activation="relu")
        self.ffn_layer_2 = layers.Dense(embed_dim)

        # Layer normalizations
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.layernorm_3 = layers.LayerNormalization()

        # Output layers
        self.embedding = PositionalEmbedding(
            embed_dim=EMBED_DIM, sequence_length=SEQ_LENGTH, vocab_size=VOCAB_SIZE
        )
        self.out = layers.Dense(VOCAB_SIZE, activation="softmax")

        # Dropout layers for regularization
        self.dropout_1 = layers.Dropout(dropout_rate)  # previously 0.1
        self.dropout_2 = layers.Dropout(dropout_rate)  # previously 0.1
        # self.supports_masking = True

    def call(self, inputs, encoder_outputs, training, mask=None):
        """
        Args:
            inputs: Tokenized inputs to the decoder (batch_size, sequence_length).
            encoder_outputs: Outputs from the encoder (batch_size, seq_len, embed_dim).
            training: Boolean indicating whether it's training or inference.
            mask: Mask for padded tokens (batch_size, sequence_length).

        Returns:
            preds: Decoder output predictions (batch_size, seq_len, vocab_size).
        """
        # logger.debug(f"Decoder Input Shape: {inputs.shape}")

        inputs = self.embedding(inputs)
        causal_mask = self.get_causal_attention_mask(inputs)

        # if mask is not None:
        #     padding_mask = tf.cast(mask[:, :, tf.newaxis], dtype=tf.int32)
        #     combined_mask = tf.cast(mask[:, tf.newaxis, :], dtype=tf.int32)
        #     combined_mask = tf.minimum(combined_mask, causal_mask)

        # Self-attention
        attention_output_1 = self.attention_1(
            query=inputs,
            value=inputs,
            key=inputs,
            attention_mask=causal_mask,
            training=training,
        )
        out_1 = self.layernorm_1(inputs + attention_output_1)

        # Cross-attention with encoder outputs
        attention_output_2 = self.attention_2(
            query=out_1,
            value=encoder_outputs,
            key=encoder_outputs,
            # attention_mask=padding_mask,
            training=training,
        )
        out_2 = self.layernorm_2(out_1 + attention_output_2)

        # Feed-forward network
        ffn_out = self.ffn_layer_1(out_2)
        ffn_out = self.dropout_1(ffn_out, training=training)
        ffn_out = self.ffn_layer_2(ffn_out)

        ffn_out = self.layernorm_3(
            ffn_out + out_2,
            # training=training
        )
        ffn_out = self.dropout_2(ffn_out, training=training)
        preds = self.out(ffn_out)

        # logger.debug(f"Decoder Output Shape: {preds.shape}")
        return preds

    def get_causal_attention_mask(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size, sequence_length = input_shape[0], input_shape[1]
        i = tf.range(sequence_length)[:, tf.newaxis]
        j = tf.range(sequence_length)
        mask = tf.cast(i >= j, dtype="int32")
        mask = tf.reshape(mask, (1, input_shape[1], input_shape[1]))
        mult = tf.concat(
            [tf.expand_dims(batch_size, -1), tf.constant([1, 1], dtype=tf.int32)],
            axis=0,
        )
        return tf.tile(mask, mult)


# Model definition
class ImageCaptioningModel(keras.Model):
    def __init__(
        self,
        cnn_model,
        encoder,
        decoder,
        num_captions_per_image=5,
        image_aug=None,
    ):
        super().__init__()
        self.cnn_model = cnn_model
        self.encoder = encoder
        self.decoder = decoder
        self.loss_tracker = keras.metrics.Mean(name="loss")
        self.acc_tracker = keras.metrics.Mean(name="accuracy")
        self.num_captions_per_image = num_captions_per_image
        self.image_aug = image_aug

    def calculate_loss(self, y_true, y_pred, mask):
        loss = self.loss(y_true, y_pred)
        mask = tf.cast(mask, dtype=loss.dtype)
        loss *= mask
        return tf.reduce_sum(loss) / tf.reduce_sum(mask)

    def calculate_accuracy(self, y_true, y_pred, mask):
        accuracy = tf.equal(y_true, tf.argmax(y_pred, axis=2))
        accuracy = tf.math.logical_and(mask, accuracy)
        accuracy = tf.cast(accuracy, dtype=tf.float32)
        mask = tf.cast(mask, dtype=tf.float32)
        return tf.reduce_sum(accuracy) / tf.reduce_sum(mask)

    def _compute_caption_loss_and_acc(self, img_embed, batch_seq, training=True):
        # logger.debug(
        #     f"Image Embedding Input Shape before passing to Encoder: {img_embed.shape}"
        # )

        # batch_seq = tf.expand_dims(batch_seq, axis=1)
        # logger.debug(f"Batch Sequence Input Shape before slicing: {batch_seq.shape}")

        encoder_out = self.encoder(img_embed, training=training)
        batch_seq_inp = batch_seq[:, :-1]  # Input sequence (without the last token)

        # logger.debug(
        #     f"Batch Sequence Input Shape before target sequence: {batch_seq_inp.shape}"
        # )

        batch_seq_true = batch_seq[:, 1:]  # Target sequence (without the first token)
        mask = tf.math.not_equal(batch_seq_true, 0)

        # logger.debug(f"Batch Sequence Input Shape: {batch_seq_inp.shape}")
        # logger.debug(f"Batch Sequence True Shape: {batch_seq_true.shape}")

        batch_seq_pred = self.decoder(
            batch_seq_inp, encoder_out, training=training, mask=mask
        )

        # logger.debug(f"Batch Sequence Predicted Shape: {batch_seq_pred.shape}")

        loss = self.calculate_loss(batch_seq_true, batch_seq_pred, mask)
        acc = self.calculate_accuracy(batch_seq_true, batch_seq_pred, mask)
        return loss, acc

    def train_step(self, batch_data):
        batch_img, batch_seq = batch_data

        # batch_seq = tf.expand_dims(batch_seq, axis=1)

        # logger.debug(
        #     f"Training Image Batch Shape before passing to CNN: {batch_img.shape}"
        # )
        total_loss = 0
        total_acc = 0

        if self.image_aug:
            batch_img = self.image_aug(batch_img)

        # logger.debug(f"Training Image Batch Shape: {batch_img.shape}")
        # logger.debug(f"Training Sequence Batch Shape: {batch_seq.shape}")

        # 1. Get image embeddings from CNN
        img_embed = self.cnn_model(batch_img)
        # logger.debug(f"Image Embeddings Shape: {img_embed.shape}")

        # 2. Reshape CNN output to (batch_size, 1, embedding_dim)
        img_embed = tf.expand_dims(img_embed, axis=1)  # It should be (None, 1, 1024)

        # logger.debug(f"Reshaped Image Embeddings for Encoder: {img_embed.shape}")

        # 3. Make sure batch_seq has 3 dimensions
        if batch_seq.shape.ndims == 2:
            # Reshape the sequence to have a third dimension (e.g., 1 caption per image)
            batch_seq = tf.expand_dims(batch_seq, axis=1)

        # logger.debug(f"Updated Sequence Shape: {batch_seq.shape}")

        # 4. Accumulate loss and accuracy for each caption
        with tf.GradientTape() as tape:
            # Loop through each caption (batch_seq should be (batch_size, num_captions, sequence_length))
            num_captions_per_image = batch_seq.shape[
                1
            ]  # Extract the num_captions dimension

            for i in range(self.num_captions_per_image):
                loss, acc = self._compute_caption_loss_and_acc(
                    img_embed, batch_seq[:, i, :], training=True
                )
                total_loss += loss
                total_acc += acc

            # 5. Compute the mean loss and accuracy
            avg_loss = total_loss / tf.cast(
                self.num_captions_per_image, dtype=tf.float32
            )
            avg_acc = total_acc / tf.cast(self.num_captions_per_image, dtype=tf.float32)

        # Backpropagation
        # 6. Get the list of all the trainable weights
        train_vars = self.encoder.trainable_variables + self.decoder.trainable_variables

        # 7. Get the gradients (from the accumulated loss)
        grads = tape.gradient(avg_loss, train_vars)

        # 8. Update the trainable weights
        self.optimizer.apply_gradients(zip(grads, train_vars))

        # 9. Update the trackers
        self.loss_tracker.update_state(avg_loss)
        self.acc_tracker.update_state(avg_acc)

        # 10. Return the loss and accuracy values
        return {"loss": self.loss_tracker.result(), "acc": self.acc_tracker.result()}

    def test_step(self, batch_data):
        batch_img, batch_seq = batch_data
        # logger.debug(f"Validation Image Batch Shape: {batch_img.shape}")
        # logger.debug(f"Validation Sequence Batch Shape: {batch_seq.shape}")

        # batch_seq = tf.expand_dims(batch_seq, axis=1)

        batch_loss = 0
        batch_acc = 0

        # 1. Get image embeddings
        img_embed = self.cnn_model(batch_img)
        logger.debug(f"Image Embeddings Shape: {img_embed.shape}")
        img_embed = tf.expand_dims(img_embed, axis=1)
        logger.debug(f"Reshaped Image Embeddings Shape: {img_embed.shape}")

        # 2. Pass each of the captions one by one to the decoder
        # along with the encoder outputs and compute the loss as well as accuracy
        # for each caption.
        # Loop through captions
        for i in range(self.num_captions_per_image):
            batch_seq_inp = batch_seq[:, i, :-1]
            batch_seq_true = batch_seq[:, i, 1:]
            # logger.debug(f"Validation Sequence Input Shape: {batch_seq_inp.shape}")
            # logger.debug(f"Validation Sequence True Shape: {batch_seq_true.shape}")

            loss, acc = self._compute_caption_loss_and_acc(
                img_embed, batch_seq[:, i, :], training=False
            )

            # 3. Update batch loss and batch accuracy
            batch_loss += loss
            batch_acc += acc

        batch_acc /= float(self.num_captions_per_image)

        # 4. Update the trackers
        self.loss_tracker.update_state(batch_loss)
        self.acc_tracker.update_state(batch_acc)

        # 5. Return the loss and accuracy values
        return {"loss": self.loss_tracker.result(), "acc": self.acc_tracker.result()}

    @property
    def metrics(self):
        # We need to list our metrics here so the `reset_states()` can be
        # called automatically.
        return [self.loss_tracker, self.acc_tracker]


# Model construction

# Initialize components
cnn_model = get_cnn_model()
encoder = TransformerEncoderBlock(embed_dim=EMBED_DIM, dense_dim=FF_DIM, num_heads=4)
decoder = TransformerDecoderBlock(embed_dim=EMBED_DIM, ff_dim=FF_DIM, num_heads=4)

# Create the ImageCaptioningModel
caption_model = ImageCaptioningModel(
    cnn_model=cnn_model,
    encoder=encoder,
    decoder=decoder,
    image_aug=image_augmentation,
)


# Load weights
def load_weights(filepath):
    # Check for the files
    try:
        # Loading weights
        fls = os.listdir(WEIGHTS_DIR)

        # Look for specific weight files (like .index or .data-00000-of-00001)
        checkpoint_files = [f for f in fls if "imgcap_" in f]

        if len(checkpoint_files) > 0:
            logger.info("Found saved weights, loading them now...")
            caption_model.load_weights(filepath)
            logger.info("Saved weights loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error loading weights: {str(e)}")


# Load weights
WEIGHTS_FILE = f"{WEIGHTS_DIR}imgcap_{mdx}"
load_weights(WEIGHTS_FILE)

# Initialize Vocabulary
try:
    vocab = vectorization.get_vocabulary() if vectorization else None
    if vocab:
        index_lookup = dict(zip(range(len(vocab)), vocab))
        logger.info(f"Vocabulary size: {len(vocab)}")
    else:
        index_lookup = None
        logger.warning("Vocabulary is missing. Captions may not generate correctly.")
except AttributeError as e:
    index_lookup = None
    logger.error(f"Failed to retrieve vocabulary: {e}")
except Exception as e:
    index_lookup = None
    logger.error(f"Unexpected error while initializing vocabulary: {e}")

max_decoded_sentence_length = SEQ_LENGTH - 1


# Generate Caption
def generate(img_path):
    """
    Generate a caption for the given image.

    Args:
    - img_path: Path to the input image.

    Returns:
    - str: The generated caption or an error message.
    """
    try:
        # Decode and resize the image
        sample_img = decode_and_resize(img_path)
        if sample_img is None:
            logger.error("Image could not be processed.")
            return "Image could not be processed."

        img = sample_img.numpy().clip(0, 255).astype(np.uint8)

        # Log the processed image
        logger.debug(f"Processed image shape: {img.shape}")
        logger.debug(f"Processed image dtype: {img.dtype}")
        logger.debug(f"Processed image pixel range: {img.min()} - {img.max()}")

        # Process the image
        # Pass the image to the CNN
        img_tensor = tf.expand_dims(sample_img, 0)
        # logger.debug(f"Image tensor shape: {img_tensor.shape}")
        img_features = caption_model.cnn_model(img_tensor)
        # logger.debug(f"Features shape after CNN: {img_features.shape}")

        # Expand dimensions to make it compatible with the encoder
        img_features = tf.expand_dims(
            img_features, 1
        )  # Adding sequence dimension, shape becomes (batch_size, 1, embed_dim)

        # Encode the image
        # Pass the image features to the Transformer encoder
        encoded_img = caption_model.encoder(img_features, training=False)

        # Decode the caption
        # Generate the caption using the Transformer decoder
        # **Optimized Caption Generation**
        decoded_caption = ["<start>"]
        for i in range(max_decoded_sentence_length):
            if vectorization is None:
                logger.error("Caption generation unavailable.")
                return "Caption generation unavailable."

            # Ensure decoded_caption is passed as a list of strings
            tokenized_caption = vectorization(tf.constant([" ".join(decoded_caption)]))[
                :, :-1
            ]
            if tokenized_caption is None or not tf.is_tensor(tokenized_caption):
                logger.error(f"Tokenization failed for caption: {decoded_caption}")
                return "Error: Tokenization failed."
            # logger.debug(f"Tokenized caption shape: {tokenized_caption.shape}")

            # Create mask for the tokenized caption
            mask = tf.math.not_equal(tokenized_caption, 0)
            if mask is None or not tf.is_tensor(mask):
                logger.error("Mask creation failed.")
                return "Error: Mask creation failed."
            # logger.debug(f"Mask shape and values: {mask.shape}, {mask}")

            predictions = caption_model.decoder(
                tokenized_caption, encoded_img, training=False, mask=mask
            )
            if predictions is None or not tf.is_tensor(predictions):
                logger.error("Decoder predictions failed.")
                return "Error: Decoder predictions failed."
            # logger.debug(f"Predictions shape: {predictions.shape}")

            # Get the predicted token
            sampled_token_index = np.argmax(predictions[0, i, :])

            # Check if token index is valid
            if sampled_token_index >= len(vocab):
                logger.warning(f"Token index {sampled_token_index} out of range.")
                continue  # Skip to the next iteration if the token is out of range

            sampled_token = index_lookup[sampled_token_index]

            if sampled_token in ("[UNK]", "<pad>", ""):
                continue  # Skip unknown tokens

            # Handle noisy or unknown tokens
            if sampled_token in ("[UNK]", ""):
                logger.warning(f"Encountered noisy token '{sampled_token}'. Skipping.")
                continue  # Skip this token

            if sampled_token == "<end>":
                break

            # **Ensure no consecutive duplicate tokens**
            if decoded_caption[-1] != sampled_token:
                decoded_caption.append(sampled_token)

        # Convert list back to string
        decoded_caption = " ".join(
            decoded_caption[1:]
        ).strip()  # Remove "<start>" and join words
        logger.info(f"Generated caption for image {img_path}: {decoded_caption}")
        return decoded_caption
    except Exception as e:
        logger.error(f"Error generating caption for image {img_path}: {e}")
        return "Error generating caption."
