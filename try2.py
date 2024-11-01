"""import numpy as np
from PIL import Image
import os
import decimal

def convert_to_float16(value):
    #Convert a decimal value to a float16 representation
    return np.float16(value)

def convert_image_to_webp(image_path, output_path):
    #Convert an image to WebP format and check memory usage
    # Open the image
    img = Image.open(image_path)
    img = img.convert("RGB")  # Ensure it's in RGB format
    data = np.array(img)

    # Memory consumption of original image
    original_size = os.path.getsize(image_path)

    # Convert pixel values to float16
    float16_data = np.array([convert_to_float16(pixel) for pixel in data.flatten()]).reshape(data.shape)

    # Save the image as WebP
    img.save(output_path, format='WEBP')

    # Memory consumption of the WebP image
    webp_size = os.path.getsize(output_path)

    # Display memory consumption
    memory_usage = {
        'original_size': original_size,
        'float16_size': float16_data.nbytes,
        'webp_size': webp_size
    }

    # Print results
    print(f"Original Image Size: {original_size} bytes")
    print(f"Converted to Float16 Size: {float16_data.nbytes} bytes")
    print(f"Saved WebP Image Size: {webp_size} bytes")
    print("Memory usage:", memory_usage)

# Example usage
input_image_path = '/home/omenyo/Documents/GitHub/Pharmacy_Management_System/output_image1.webp'  # Replace with your image file path
output_image_path = 'output_image1.webp'  # Desired output file path

convert_image_to_webp(input_image_path, output_image_path)
"""
"""from PIL import Image

# Open a 24-bit image
img = Image.open("/home/omenyo/Documents/GitHub/Pharmacy_Management_System/output_image1.webp")

# Convert to 8-bit
img = img.convert("P", palette=Image.ADAPTIVE, colors=2)

# Save the new image
img.save("example_image_8bit.png")
"""
from PIL import Image


# Open an image
original_image = Image.open("/home/omenyo/Documents/GitHub/Pharmacy_Management_System/logon_lps.jpg")

# Resize to a smaller version
small_image = original_image.resize((original_image.width // 2, original_image.height // 2))
small_image.save("/home/omenyo/Documents/GitHub/Pharmacy_Management_System/small_image.jpg", "JPEG")

# Convert back to original size
restored_image = small_image.resize((original_image.width, original_image.height))
restored_image.save("/home/omenyo/Documents/GitHub/Pharmacy_Management_System/restored_image.jpg", "JPEG")
from PIL import Image

# Function to upscale the image using a high-quality interpolation method
def enhance_resolution(input_path, output_path, upscale_factor=8):
    # Open the image
    image = Image.open(input_path)

    # Calculate the new size (scaling the image by the upscale factor)
    new_size = (int(image.width * upscale_factor), int(image.height * upscale_factor))

    # Resize the image using a high-quality resampling method (e.g., Lanczos)
    enhanced_image = image.resize(new_size, Image.BICUBIC)#Image.LANCZOS)

    # Save the enhanced image
    enhanced_image.save(output_path, format='JPEG')
    print(f"Enhanced image saved as {output_path}")

# Example usage
input_path = '/home/omenyo/Documents/GitHub/Pharmacy_Management_System/logon_lps.jpg'
output_path = '/home/omenyo/Documents/GitHub/Pharmacy_Management_System/enhanced_image.jpg'
enhance_resolution(input_path, output_path, upscale_factor=2)
