import os
import tempfile
import numpy as np
from flask import current_app
import speech_recognition as sr
from pydub import AudioSegment

def transcribe_audio(audio_path):
    """Transcribe audio file to text using Whisper or DeepSpeech alternative"""
    try:
        # Try to use transformers for Whisper
        from transformers import pipeline
        
        transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-small")
        result = transcriber(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error using Whisper: {e}")
        # Fallback to SpeechRecognition
        return fallback_transcribe_audio(audio_path)

def fallback_transcribe_audio(audio_path):
    """Fallback transcription using SpeechRecognition library"""
    # Convert to WAV if not already in that format
    if not audio_path.lower().endswith('.wav'):
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + ".wav"
        audio.export(wav_path, format="wav")
        audio_path = wav_path
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error with SpeechRecognition: {e}")
        return "Transcription unavailable."

def text_to_speech(text, content_id):
    """Convert text to speech using Coqui TTS or alternative"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    output_path = os.path.join(upload_folder, f"speech_{content_id}.wav")
    
    try:
        # Try to use transformers for TTS
        from transformers import pipeline
        
        synthesizer = pipeline("text-to-speech")
        speech = synthesizer(text)
        
        with open(output_path, "wb") as f:
            f.write(speech["bytes"])
        
        return output_path
    except Exception as e:
        print(f"Error using transformer TTS: {e}")
        # Fallback to a simple beep pattern
        return generate_fallback_audio(text, output_path)

def generate_fallback_audio(text, output_path, duration=5):
    """Generate a simple audio file with beeps as a fallback"""
    try:
        from scipy.io import wavfile
        import scipy.signal
        
        # Generate a simple audio signal
        sample_rate = 22050
        t = np.linspace(0, duration, sample_rate * duration)
        
        # Create a beep for each word
        words = text.split()
        signal = np.zeros_like(t)
        
        beeps_per_second = min(len(words) / duration, 4)  # Max 4 beeps per second
        
        for i in range(min(len(words), int(beeps_per_second * duration))):
            # Position in the audio
            pos = i / beeps_per_second
            # Generate a short beep
            idx = (t >= pos) & (t < pos + 0.1)
            signal[idx] = 0.5 * np.sin(2 * np.pi * 440 * (t[idx] - pos))
        
        # Normalize and convert to int16
        signal = np.int16(signal * 32767)
        
        # Save to WAV file
        wavfile.write(output_path, sample_rate, signal)
        
        return output_path
    except Exception as e:
        print(f"Error generating fallback audio: {e}")
        
        # Create an empty audio file
        with open(output_path, 'wb') as f:
            # Create a minimal WAV header
            f.write(b'RIFF')
            f.write((36).to_bytes(4, byteorder='little'))  # File size - 8
            f.write(b'WAVE')
            
            # Format chunk
            f.write(b'fmt ')
            f.write((16).to_bytes(4, byteorder='little'))  # Chunk size
            f.write((1).to_bytes(2, byteorder='little'))   # PCM format
            f.write((1).to_bytes(2, byteorder='little'))   # Mono
            f.write((22050).to_bytes(4, byteorder='little'))  # Sample rate
            f.write((22050 * 2).to_bytes(4, byteorder='little'))  # Byte rate
            f.write((2).to_bytes(2, byteorder='little'))   # Block align
            f.write((16).to_bytes(2, byteorder='little'))  # Bits per sample
            
            # Data chunk
            f.write(b'data')
            f.write((0).to_bytes(4, byteorder='little'))   # Data size
        
        return output_path
