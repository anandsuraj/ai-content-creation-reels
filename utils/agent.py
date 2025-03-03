import os
from flask import current_app
from ai_content_platform import db
from ai_content_platform.models.content import Content
from ai_content_platform.utils.text_utils import generate_text_prompt, auto_complete
from ai_content_platform.utils.image_utils import generate_photo_quote
from ai_content_platform.utils.video_utils import generate_video_reel, generate_avatar_video
from ai_content_platform.utils.audio_utils import text_to_speech

class ContentAgent:
    """Agent to orchestrate content creation and transformation tasks"""
    
    def __init__(self):
        """Initialize the content agent"""
        pass
    
    def remix_content(self, content_item, target_format):
        """Remix existing content into a new format"""
        # Create a new content item
        new_content = Content(
            title=f"Remix of {content_item.title}",
            content_type=target_format,
            input_text=content_item.input_text,
            user_id=content_item.user_id
        )
        
        # Add to database to get an ID
        db.session.add(new_content)
        db.session.commit()
        
        # Generate content based on target format
        if target_format == 'photo_quote':
            output_path = generate_photo_quote(content_item.input_text, new_content.id)
            new_content.output_path = output_path
            
        elif target_format == 'video_reel':
            output_path = generate_video_reel(content_item.input_text, new_content.id)
            new_content.output_path = output_path
            
        elif target_format == 'avatar_video':
            # Generate speech from text
            audio_path = text_to_speech(content_item.input_text, new_content.id)
            
            # Generate avatar video
            output_path = generate_avatar_video(content_item.input_text, new_content.id, audio_path=audio_path)
            new_content.output_path = output_path
            
        # Save changes
        db.session.commit()
        
        return new_content
    
    def generate_content_calendar(self, user_id, days=7):
        """Generate a content calendar with suggested topics"""
        calendar = []
        
        # Get user's recent content for analysis
        recent_content = Content.query.filter_by(user_id=user_id).order_by(Content.created_at.desc()).limit(10).all()
        
        # Extract themes from recent content
        themes = []
        for content in recent_content:
            if content.input_text:
                themes.extend(content.input_text.split())
        
        # Filter and process themes
        if themes:
            # Simple frequency analysis
            from collections import Counter
            word_counts = Counter(themes)
            common_words = [word for word, count in word_counts.most_common(5)]
            
            # Generate prompts based on common themes
            theme_str = " ".join(common_words)
            prompts = generate_text_prompt(theme_str, count=days)
        else:
            # Default prompts if no themes found
            prompts = generate_text_prompt("inspiration", count=days)
        
        # Create calendar entries
        import datetime
        today = datetime.date.today()
        
        content_types = ['photo_quote', 'video_reel', 'avatar_video']
        
        for i, prompt in enumerate(prompts):
            date = today + datetime.timedelta(days=i)
            calendar.append({
                'date': date.isoformat(),
                'suggestion': prompt,
                'content_type': content_types[i % len(content_types)]
            })
        
        return calendar
    
    def optimize_content(self, content_item, platform):
        """Optimize content for a specific platform"""
        # This would implement platform-specific optimizations
        # For demonstration purposes, we'll return some basic recommendations
        
        recommendations = {
            'instagram': {
                'aspect_ratio': '1:1 for feed, 9:16 for stories',
                'optimal_length': '30 seconds for reels',
                'hashtags': '#content #ai #digital'
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'optimal_length': 'Under 2 minutes for videos',
                'hashtags': '#AIcontent #digital #creator'
            },
            'tiktok': {
                'aspect_ratio': '9:16',
                'optimal_length': '15-60 seconds',
                'hashtags': '#fyp #aicontent #creator'
            }
        }
        
        if platform.lower() in recommendations:
            return recommendations[platform.lower()]
        else:
            return {
                'aspect_ratio': '16:9',
                'optimal_length': '1-2 minutes',
                'hashtags': '#content #digital #ai'
            }
