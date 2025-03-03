import os
import tempfile
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import ffmpeg
from flask import current_app

from ai_content_platform.utils.image_utils import generate_background, create_gradient_background

def generate_video_reel(text, content_id, duration=15, fps=30, audio_path=None):
    """Generate a video reel with text overlay and optional audio"""
    # Create output paths
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    background_path = os.path.join(upload_folder, f"background_{content_id}.jpg")
    frames_dir = os.path.join(upload_folder, f"frames_{content_id}")
    os.makedirs(frames_dir, exist_ok=True)
    
    output_path = os.path.join(upload_folder, f"video_{content_id}.mp4")
    
    # Generate background image
    prompt = f"Cinematic scene for video about: {text[:50]}"
    generate_background(prompt, background_path)
    
    # Create frames with text animation
    total_frames = duration * fps
    
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Open background image
    try:
        background = Image.open(background_path)
    except Exception as e:
        print(f"Error opening background image: {e}")
        create_gradient_background(background_path)
        background = Image.open(background_path)
    
    # Resize to standard video dimensions (1080p)
    width, height = 1920, 1080
    background = background.resize((width, height), Image.LANCZOS)
    
    # Split text into words for animation
    words = text.split()
    
    # Calculate frames per word
    frames_per_word = min(30, total_frames // max(1, len(words)))
    
    # Generate frames
    frame_count = 0
    for i, word in enumerate(words):
        # Position for this word (centered with some randomness)
        x_pos = width // 2 + random.randint(-200, 200)
        y_pos = height // 2 + random.randint(-100, 100)
        
        # How many frames to show this word
        word_frames = min(frames_per_word, total_frames - frame_count)
        
        for f in range(word_frames):
            # Create a new frame from the background
            frame = background.copy()
            draw = ImageDraw.Draw(frame)
            
            # Calculate animation effects (fade in/out)
            opacity = 255
            if f < 5:  # Fade in
                opacity = int(255 * (f / 5))
            elif f > word_frames - 5:  # Fade out
                opacity = int(255 * ((word_frames - f) / 5))
            
            # Draw word with current opacity
            draw.text((x_pos, y_pos), word, fill=(255, 255, 255, opacity), font=font)
            
            # Add previous words with full opacity
            if i > 0:
                prev_text = " ".join(words[:i])
                draw.text((width//2 - 200, height - 200), prev_text, fill=(255, 255, 255, 255), font=font)
            
            # Save the frame
            frame_path = os.path.join(frames_dir, f"frame_{frame_count:04d}.jpg")
            frame.save(frame_path)
            frame_count += 1
            
            # Break if we've generated all needed frames
            if frame_count >= total_frames:
                break
        
        if frame_count >= total_frames:
            break
    
    # If we didn't generate enough frames, duplicate the last frame
    last_frame_path = os.path.join(frames_dir, f"frame_{frame_count-1:04d}.jpg")
    while frame_count < total_frames:
        frame_path = os.path.join(frames_dir, f"frame_{frame_count:04d}.jpg")
        os.system(f"cp {last_frame_path} {frame_path}")
        frame_count += 1
    
    # Combine frames into video
    frame_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
    
    # Use ffmpeg to create video
    if audio_path:
        # With audio
        os.system(f"ffmpeg -y -framerate {fps} -i {frame_pattern} -i {audio_path} -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_path}")
    else:
        # Without audio
        os.system(f"ffmpeg -y -framerate {fps} -i {frame_pattern} -c:v libx264 -pix_fmt yuv420p {output_path}")
    
    # Clean up temporary files
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)
    
    return output_path

def generate_avatar_video(text, content_id, audio_path=None, avatar_type="default"):
    """Generate a video with an animated avatar speaking the given text or audio"""
    # Create output paths
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    output_path = os.path.join(upload_folder, f"avatar_{content_id}.mp4")
    
    # For demonstration purposes, we'll create a simple animation
    # In a real implementation, we would use SadTalker, EchoMimic, or similar
    
    # Create a simple background
    width, height = 1280, 720
    background_color = (50, 50, 100)  # Dark blue background
    
    # Create frame directory
    frames_dir = os.path.join(upload_folder, f"avatar_frames_{content_id}")
    os.makedirs(frames_dir, exist_ok=True)
    
    # Determine video duration based on audio or text length
    if audio_path:
        # Get audio duration using ffmpeg
        probe = ffmpeg.probe(audio_path)
        audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        duration = float(audio_info['duration'])
    else:
        # Estimate duration based on text length (approx. 3 words per second)
        word_count = len(text.split())
        duration = max(3, word_count / 3)  # At least 3 seconds
    
    # Determine frame count
    fps = 30
    total_frames = int(duration * fps)
    
    # Generate frames
    for i in range(total_frames):
        # Create blank frame
        frame = np.ones((height, width, 3), dtype=np.uint8) * np.array(background_color, dtype=np.uint8)
        
        # Calculate animation time (0 to 1)
        t = i / total_frames
        
        # Draw a simple avatar (circle with features)
        # In a real implementation, this would be a proper 3D model with lip syncing
        cv2.circle(frame, (width//2, height//3), 100, (200, 200, 200), -1)  # Head
        
        # Eyes
        eye_y = height//3 - 20
        left_eye_x = width//2 - 30
        right_eye_x = width//2 + 30
        
        # Animate the eyes (blink occasionally)
        if i % 100 > 95:  # Blink every 100 frames for 5 frames
            cv2.line(frame, (left_eye_x-10, eye_y), (left_eye_x+10, eye_y), (0, 0, 0), 2)
            cv2.line(frame, (right_eye_x-10, eye_y), (right_eye_x+10, eye_y), (0, 0, 0), 2)
        else:
            cv2.circle(frame, (left_eye_x, eye_y), 5, (0, 0, 0), -1)
            cv2.circle(frame, (right_eye_x, eye_y), 5, (0, 0, 0), -1)
        
        # Mouth animation
        mouth_y = height//3 + 30
        mouth_x = width//2
        
        # Animate the mouth (open and close)
        # This would be synchronized with audio in a real implementation
        mouth_open = 10 + int(10 * np.sin(i * 0.2))  # Simple oscillation for mouth movement
        cv2.ellipse(frame, (mouth_x, mouth_y), (30, mouth_open), 0, 0, 180, (0, 0, 0), -1)
        
        # Add text caption at the bottom
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get portion of text to display based on current time
        text_position = min(len(text), int(len(text) * t * 1.2))
        current_text = text[:text_position]
        
        # Split into lines if too long
        max_line_length = 50
        lines = []
        for j in range(0, len(current_text), max_line_length):
            lines.append(current_text[j:j+max_line_length])
        
        # Draw each line
        for idx, line in enumerate(lines):
            y_position = height - 100 + (idx * 30)
            cv2.putText(frame, line, (50, y_position), font, 0.7, (255, 255, 255), 2)
        
        # Save the frame
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.jpg")
        cv2.imwrite(frame_path, frame)
    
    # Combine frames into video
    frame_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
    
    # Use ffmpeg to create video
    if audio_path:
        # With audio
        os.system(f"ffmpeg -y -framerate {fps} -i {frame_pattern} -i {audio_path} -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_path}")
    else:
        # Without audio
        os.system(f"ffmpeg -y -framerate {fps} -i {frame_pattern} -c:v libx264 -pix_fmt yuv420p {output_path}")
    
    # Clean up temporary files
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)
    
    return output_path
