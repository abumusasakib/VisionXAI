import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ImgCap import captioner as cap
from loguru import logger

# Configure logging with loguru
LOG_FILE = "app.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup log files

logger.add(
    LOG_FILE, 
    rotation="1 day",  # Rotate log every day
    retention="7 days",  # Keep logs for the last 7 days
    compression="zip",  # Compress old log files
    level="INFO",  # Default log level
)

logger.add(
    "stdout", 
    level="INFO",  # Console log level
)

# Initialize the FastAPI app
app = FastAPI(
    title="Image Caption Generation API",
    description="An API for generating image captions in Bengali.",
    version="1.0.0"
)

# Configure upload folder
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"Upload folder initialized at {UPLOAD_FOLDER}")

# Allow CORS for flexibility in development/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Routes and Endpoints

@app.get("/", response_model=dict)
def read_root():
    """
    Root endpoint to confirm the API is live.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Image Caption Generation in Bengali"}

@app.post("/upload", response_model=dict)
async def upload_image(image: UploadFile = File(...)):
    """
    Endpoint to upload an image. Replaces any existing image in the upload folder.
    """
    logger.info("Upload endpoint called")
    if not image.filename:
        logger.warning("No file selected by the user")
        raise HTTPException(status_code=400, detail="No file selected.")
    
    extension = image.filename.split(".")[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        logger.warning(f"Invalid file format: {extension}")
        raise HTTPException(status_code=400, detail="Invalid file format. Only jpg, jpeg, png are supported.")

    # Clear the upload folder
    logger.info("Clearing existing files in the upload folder")
    for item in os.listdir(UPLOAD_FOLDER):
        item_path = os.path.join(UPLOAD_FOLDER, item)
        if os.path.isfile(item_path):
            os.remove(item_path)

    # Save the new image
    file_path = os.path.join(UPLOAD_FOLDER, f"image.{extension}")
    with open(file_path, "wb") as f:
        f.write(await image.read())
    
    logger.info(f"Image uploaded successfully: {file_path}")
    return {"message": "Image uploaded successfully.", "filename": file_path}

@app.get("/caption", response_model=dict)
def generate_caption():
    """
    Endpoint to generate a caption for the uploaded image.
    """
    logger.info("Caption generation endpoint called")
    # Check if there's an uploaded image
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        logger.warning("No uploaded image found when attempting to generate a caption")
        raise HTTPException(status_code=400, detail="No image found. Please upload an image first.")
    
    image_name = files[0]  # There should be only one file in the folder
    image_path = os.path.join(UPLOAD_FOLDER, image_name)

    # Generate the caption
    try:
        logger.info(f"Generating caption for image: {image_path}")
        caption = cap.generate(image_path)
    except Exception as e:
        logger.error(f"Caption generation failed for {image_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")
    
    logger.info(f"Caption generated successfully for {image_path}")
    return {"image": image_name, "caption": caption}

# Run the app
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the API server")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
