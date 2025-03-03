from datetime import datetime
import json
from ai_content_platform import db

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # photo_quote, video_reel, voice_video, avatar_video
    input_text = db.Column(db.Text, nullable=True)
    
    # Output paths
    output_path = db.Column(db.String(500), nullable=True)
    thumbnail_path = db.Column(db.String(500), nullable=True)
    
    # Metadata (stored as JSON)
    metadata = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def set_metadata(self, metadata_dict):
        self.metadata = json.dumps(metadata_dict)
        
    def get_metadata(self):
        if self.metadata:
            return json.loads(self.metadata)
        return {}
    
    def __repr__(self):
        return f'<Content {self.title}>'
