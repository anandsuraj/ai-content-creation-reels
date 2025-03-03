import random
import os
from transformers import pipeline

# Mock function for generating text prompts
# In a production environment, this would use a proper NLP model
def generate_text_prompt(theme, count=3):
    """Generate creative text prompts based on a theme"""
    
    # For demonstration purposes, return some pre-defined prompts
    prompts_by_theme = {
        'inspiration': [
            "The journey of a thousand miles begins with a single step.",
            "Believe you can and you're halfway there.",
            "You are never too old to set another goal or to dream a new dream.",
            "The only way to do great work is to love what you do."
        ],
        'motivation': [
            "Success is not final, failure is not fatal: It is the courage to continue that counts.",
            "Don't watch the clock; do what it does. Keep going.",
            "The future belongs to those who believe in the beauty of their dreams.",
            "You are capable of more than you know."
        ],
        'creativity': [
            "Creativity is intelligence having fun.",
            "The creative adult is the child who survived.",
            "You can't use up creativity. The more you use, the more you have.",
            "Creativity takes courage."
        ]
    }
    
    # Default to a mix if theme not specified
    if not theme or theme not in prompts_by_theme:
        all_prompts = []
        for t in prompts_by_theme:
            all_prompts.extend(prompts_by_theme[t])
        return random.sample(all_prompts, min(count, len(all_prompts)))
    
    # Return prompts for the specified theme
    theme_prompts = prompts_by_theme[theme]
    return random.sample(theme_prompts, min(count, len(theme_prompts)))

# Function to check if transformers is available and generate a caption
def generate_caption(image_path):
    """Generate a caption for an image"""
    try:
        # Try to import and use the transformers library
        image_to_text = pipeline("image-to-text")
        result = image_to_text(image_path)
        return result[0]['generated_text']
    except Exception as e:
        print(f"Error generating caption: {e}")
        return "A beautiful image."

# Function to generate a completion based on input text
def auto_complete(text, max_length=50):
    """Generate text completion based on input"""
    try:
        # Try to use the transformers library for text generation
        generator = pipeline('text-generation')
        result = generator(text, max_length=max_length, num_return_sequences=1)
        return result[0]['generated_text']
    except Exception as e:
        print(f"Error in text completion: {e}")
        # Fallback simple completion
        completions = {
            "I feel": " happy today because the sun is shining.",
            "The best way": " to learn is by doing.",
            "Remember": " to always be kind to yourself.",
            "Life is": " a journey, not a destination."
        }
        
        for starter in completions:
            if text.startswith(starter):
                return text + completions[starter]
        
        return text + "... (completion not available)"
