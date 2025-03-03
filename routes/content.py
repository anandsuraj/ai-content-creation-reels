import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ai_content_platform import db
from ai_content_platform.models.content import Content
from ai_content_platform.utils.text_utils import generate_text_prompt
from ai_content_platform.utils.image_utils import generate_photo_quote
from ai_content_platform.utils.video_utils import generate_video_reel, generate_avatar_video
from ai_content_platform.utils.audio_utils import transcribe_audio, text_to_speech
from ai_content_platform.utils.agent import ContentAgent

content = Blueprint('content', __name__)

@content.route('/')
def index():
    return render_template('index.html')

@content.route('/dashboard')
@login_required
def dashboard():
    user_content = Content.query.filter_by(user_id=current_user.id).order_by(Content.created_at.desc()).all()
    return render_template('dashboard.html', content_items=user_content)

@content.route('/create', methods=['GET', 'POST'])
@login_required
def create_content():
    if request.method == 'POST':
        content_type = request.form['content_type']
        title = request.form['title']
        
        new_content = Content(
            title=title,
            content_type=content_type,
            user_id=current_user.id
        )
        
        # Handle different content types
        if content_type == 'photo_quote':
            text = request.form['input_text']
            new_content.input_text = text
            
            # Save to get an ID
            db.session.add(new_content)
            db.session.commit()
            
            # Generate the content
            output_path = generate_photo_quote(text, new_content.id)
            new_content.output_path = output_path
            new_content.set_metadata({
                'font': 'default',
                'style': 'modern',
                'colors': 'auto'
            })
            
        elif content_type == 'video_reel':
            text = request.form['input_text']
            new_content.input_text = text
            
            # Save to get an ID
            db.session.add(new_content)
            db.session.commit()
            
            # Generate the content
            output_path = generate_video_reel(text, new_content.id)
            new_content.output_path = output_path
            new_content.set_metadata({
                'duration': '15s',
                'style': 'dynamic',
                'music': 'auto'
            })
            
        elif content_type == 'voice_video':
            # Handle audio file upload
            if 'audio_file' not in request.files:
                flash('No audio file uploaded')
                return redirect(request.url)
            
            audio_file = request.files['audio_file']
            if audio_file.filename == '':
                flash('No audio file selected')
                return redirect(request.url)
            
            # Save audio file
            audio_filename = secure_filename(audio_file.filename)
            audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"audio_{current_user.id}_{audio_filename}")
            audio_file.save(audio_path)
            
            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            new_content.input_text = transcription
            
            # Save to get an ID
            db.session.add(new_content)
            db.session.commit()
            
            # Generate video with captions
            output_path = generate_video_reel(transcription, new_content.id, audio_path=audio_path)
            new_content.output_path = output_path
            new_content.set_metadata({
                'audio_path': audio_path,
                'transcription': transcription,
                'style': 'scenic'
            })
            
        elif content_type == 'avatar_video':
            if 'audio_file' in request.files and request.files['audio_file'].filename != '':
                # Use uploaded audio file
                audio_file = request.files['audio_file']
                audio_filename = secure_filename(audio_file.filename)
                audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"audio_{current_user.id}_{audio_filename}")
                audio_file.save(audio_path)
                
                # Transcribe audio
                transcription = transcribe_audio(audio_path)
                new_content.input_text = transcription
                
                # Save to get an ID
                db.session.add(new_content)
                db.session.commit()
                
                # Generate avatar video
                output_path = generate_avatar_video(transcription, new_content.id, audio_path=audio_path)
                
            else:
                # Use text-to-speech
                text = request.form['input_text']
                new_content.input_text = text
                
                # Save to get an ID
                db.session.add(new_content)
                db.session.commit()
                
                # Generate speech from text
                audio_path = text_to_speech(text, new_content.id)
                
                # Generate avatar video
                output_path = generate_avatar_video(text, new_content.id, audio_path=audio_path)
                
            new_content.output_path = output_path
            new_content.set_metadata({
                'avatar_style': 'realistic',
                'voice_style': 'natural',
                'background': 'gradient'
            })
            
        # Final save
        db.session.commit()
        flash('Content created successfully!')
        return redirect(url_for('content.view_content', content_id=new_content.id))
        
    return render_template('content_creation.html')

@content.route('/content/<int:content_id>')
@login_required
def view_content(content_id):
    content_item = Content.query.get_or_404(content_id)
    
    # Security check to ensure the user owns this content
    if content_item.user_id != current_user.id:
        flash('You do not have permission to view this content.')
        return redirect(url_for('content.dashboard'))
    
    return render_template('content_detail.html', content=content_item)

@content.route('/content/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    content_item = Content.query.get_or_404(content_id)
    
    # Security check to ensure the user owns this content
    if content_item.user_id != current_user.id:
        flash('You do not have permission to delete this content.')
        return redirect(url_for('content.dashboard'))
    
    # Delete associated files
    if content_item.output_path and os.path.exists(content_item.output_path):
        os.remove(content_item.output_path)
    
    if content_item.thumbnail_path and os.path.exists(content_item.thumbnail_path):
        os.remove(content_item.thumbnail_path)
    
    # Delete from database
    db.session.delete(content_item)
    db.session.commit()
    
    flash('Content deleted successfully.')
    return redirect(url_for('content.dashboard'))
