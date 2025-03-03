from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user

from ai_content_platform import db
from ai_content_platform.models.content import Content
from ai_content_platform.utils.text_utils import generate_text_prompt
from ai_content_platform.utils.agent import ContentAgent

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/generate-prompts', methods=['POST'])
@login_required
def generate_prompts():
    data = request.get_json()
    theme = data.get('theme', '')
    count = data.get('count', 3)
    
    prompts = generate_text_prompt(theme, count)
    
    return jsonify({
        'success': True,
        'prompts': prompts
    })

@api.route('/content/<int:content_id>', methods=['GET'])
@login_required
def get_content(content_id):
    content_item = Content.query.get_or_404(content_id)
    
    # Security check
    if content_item.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You do not have permission to access this content.'
        }), 403
    
    return jsonify({
        'success': True,
        'content': {
            'id': content_item.id,
            'title': content_item.title,
            'content_type': content_item.content_type,
            'input_text': content_item.input_text,
            'output_path': content_item.output_path,
            'thumbnail_path': content_item.thumbnail_path,
            'created_at': content_item.created_at.isoformat(),
            'updated_at': content_item.updated_at.isoformat(),
            'metadata': content_item.get_metadata()
        }
    })

@api.route('/remix/<int:content_id>', methods=['POST'])
@login_required
def remix_content(content_id):
    content_item = Content.query.get_or_404(content_id)
    
    # Security check
    if content_item.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You do not have permission to access this content.'
        }), 403
    
    data = request.get_json()
    target_format = data.get('target_format')
    
    # Initialize the agent
    agent = ContentAgent()
    
    # Get remixed content
    remixed_content = agent.remix_content(content_item, target_format)
    
    return jsonify({
        'success': True,
        'new_content_id': remixed_content.id
    })

@api.route('/content-calendar', methods=['GET'])
@login_required
def get_content_calendar():
    calendar = [
        {
            'date': '2023-04-01',
            'suggestion': 'Create a quote about spring renewal',
            'content_type': 'photo_quote'
        },
        {
            'date': '2023-04-03',
            'suggestion': 'Share a short video about your creative process',
            'content_type': 'video_reel'
        },
        {
            'date': '2023-04-05',
            'suggestion': 'Record a voice message for your audience',
            'content_type': 'voice_video'
        }
    ]
    
    return jsonify({
        'success': True,
        'calendar': calendar
    })
