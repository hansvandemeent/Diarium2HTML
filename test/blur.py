import cv2
import os

# Source and destination folders
SOURCE_FOLDER = 'media-org'
DEST_FOLDER = 'media'

# Supported image extensions
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

def blur_image(input_path, output_path):
    image = cv2.imread(input_path)
    if image is not None:
        blurred = cv2.GaussianBlur(image, (151, 151), 0)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, blurred)
        print(f"Blurred: {output_path}")
    else:
        print(f"Failed to load: {input_path}")

def process_images():
    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, SOURCE_FOLDER)
                output_path = os.path.join(DEST_FOLDER, relative_path)
                blur_image(input_path, output_path)

# Run the script
process_images()