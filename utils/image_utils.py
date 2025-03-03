import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from flask import current_app

# Mock function for Stable Diffusion
# In a production environment, this would use the actual Stable Diffusion model
def generate_background(prompt, output_path):
    """Generate a background image based on a text prompt using Stable Diffusion"""
    try:
        # Try to import and use diffusers for Stable Diffusion
        from diffusers import StableDiffusionPipeline
        import torch
        
        # Initialize the pipeline
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Generate the image
        image = pipe(prompt).images[0]
        
        # Save the image
        image.save(output_path)
        return True
    except Exception as e:
        print(f"Error using Stable Diffusion: {e}")
        # Fallback to creating a gradient background
        create_gradient_background(output_path)
        return False

def create_gradient_background(output_path, width=1080, height=1080):
    """Create a gradient background as a fallback"""
    # Create a gradient array
    gradient = np.zeros((height, width, 3), np.uint8)
    
    # Choose random colors for top and bottom of gradient
    color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # Create gradient
    for y in range(height):
        for x in range(width):
            gradient[y, x] = [
                int(color1[0] + (color2[0] - color1[0]) * y / height),
                int(color1[1] + (color2[1] - color1[1]) * y / height),
                int(color1[2] + (color2[2] - color1[2]) * y / height)
            ]
    
    # Convert to PIL Image and save
    img = Image.fromarray(gradient)
    img.save(output_path)

def generate_photo_quote(text, content_id, width=1080, height=1080):
    """Generate a photo quote with text overlay on a background"""
    # Create the output directory if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Define output paths
    background_path = os.path.join(upload_folder, f"background_{content_id}.jpg")
    output_path = os.path.join(upload_folder, f"quote_{content_id}.jpg")
    
    # Generate or create background
    prompt = f"Abstract background for quote: {text[:50]}"
    generate_background(prompt, background_path)
    
    # Open the background image
    try:
        img = Image.open(background_path)
    except Exception as e:
        print(f"Error opening background image: {e}")
        create_gradient_background(background_path)
        img = Image.open(background_path)
    
    # Resize if needed
    if img.width != width or img.height != height:
        img = img.resize((width, height), Image.LANCZOS)
    
    # Create draw object
    draw = ImageDraw.Draw(img)
    
    # Prepare the text
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Calculate text position (centered)
    text_width, text_height = draw.textsize(text, font)
    position = ((width - text_width) / 2, (height - text_height) / 2)
    
    # Add some padding/background for text readability
    padding = 20
    draw.rectangle(
        [
            position[0] - padding, 
            position[1] - padding, 
            position[0] + text_width + padding, 
            position[1] + text_height + padding
        ], 
        fill=(0, 0, 0, 128)
    )
    
    # Draw the text
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Add a subtle watermark
    watermark = "Created with AI Content Platform"
    watermark_font = ImageFont.load_default()
    draw.text((10, height - 20), watermark, fill=(255, 255, 255, 128), font=watermark_font)
    
    # Save the final image
    img.save(output_path)
    
    # Return the path to the generated image
    return output_path
