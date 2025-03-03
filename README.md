# AI Content Creation Platform

A Flask-based web application that leverages AI to generate various types of content including photo quotes, video reels, voice videos, and avatar videos.

## Features

- **Photo Quotes**: Transform text into beautiful quote images with AI-generated backgrounds
- **Video Reels**: Create engaging video reels with text animations and music
- **Voice Videos**: Convert voice recordings into captivating videos with captions
- **Avatar Videos**: Generate videos with AI avatars that speak your text
- **Content Dashboard**: Manage and organize all your generated content
- **User Authentication**: Secure user accounts and content management

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Python 3.x
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML**: 
  - transformers (for text generation)
  - diffusers (for image generation)
  - SpeechRecognition (for audio processing)
  - OpenCV (for video processing)
  - ffmpeg-python (for media processing)

## Project Structure

```
ai-content-creation-reels/
├── models/
│   ├── __init__.py
│   ├── content.py  # Content model
│   └── user.py     # User model
│
├── routes/
│   ├── __init__.py
│   ├── api.py      # API endpoints
│   ├── auth.py     # Authentication routes
│   └── content.py  # Content management routes
│
├── static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── uploads/
│
├── templates/
│   ├── base.html
│   ├── content_creation.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── utils/
│   └── __init__.py
│
├── .gitignore
├── app.py          # Application entry point
├── config.py       # Application configuration
├── LICENSE
├── README.md
└── requirements.txt # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-content-creation-reels.git
cd ai-content-creation-reels
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

1. Configure the following environment variables:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///content_platform.db
OPENAI_API_KEY=your-openai-key
REPLICATE_API_KEY=your-replicate-key
```

2. Initialize the database:
```bash
flask db upgrade
```

## Usage

1. Start the development server:
```bash
python app.py
```

Access the application at [http://localhost:5000](http://localhost:5000)

Register a new account and start creating content!

## Development

### Running Tests
```bash
pytest
```

### Adding New Features
1. Create a new branch for your feature
2. Implement the feature
3. Write tests
4. Submit a pull request

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.