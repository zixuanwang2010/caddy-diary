import os
import sys
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash, jsonify, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from textblob import TextBlob
import nltk
from nltk.tokenize import sent_tokenize
import re
from collections import defaultdict
import subprocess
import requests
import whisper
import io
import soundfile as sf

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from config import ELEVENLABS_API_KEY, HUGGINGFACE_API_KEY
from local_summary import generate_local_summary
from gemini_summary import generate_summary_with_gemini
from cohere_summary import generate_summary_with_cohere, generate_advice_with_cohere
from questions import questions
from models import db, User, DiaryEntry, VerificationCode
from email_service import EmailService

# Optional transformers import - will be imported only when needed
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: transformers library not available. Some AI features will be disabled.")
    TRANSFORMERS_AVAILABLE = False

# Optional torch import - will be imported only when needed
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: torch library not available. Some AI features will be disabled.")
    TORCH_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Use PostgreSQL for Vercel (or SQLite for development)
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Convert postgres:// to postgresql:// for SQLAlchemy
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///caddy_diary.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure Flask for Vercel
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = False  # Set to False for production
app.config['TESTING'] = False
app.config['TRAP_HTTP_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# Voice settings for ElevenLabs
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Clear, professional voice

# Initialize Whisper model (lazy loading)
model = None

# Initialize Hugging Face pipelines (lazy loading)
summarizer = None
sentiment_analyzer = None

def get_whisper_model():
    """Lazy load Whisper model only when needed"""
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base", device="cpu")  # Use base model for Vercel
        print("Whisper model loaded!")
    return model

def get_summarizer():
    """Lazy load summarizer only when needed"""
    global summarizer
    if not TRANSFORMERS_AVAILABLE:
        print("Transformers not available, skipping summarizer loading")
        return None
    if summarizer is None:
        try:
            print("Loading summarizer...")
            summarizer = pipeline("summarization", model="facebook/bart-base-cnn")
            print("Summarizer loaded!")
        except Exception as e:
            print(f"Failed to load summarizer: {e}")
            return None
    return summarizer

def get_sentiment_analyzer():
    """Lazy load sentiment analyzer only when needed"""
    global sentiment_analyzer
    if not TRANSFORMERS_AVAILABLE:
        print("Transformers not available, skipping sentiment analyzer loading")
        return None
    if sentiment_analyzer is None:
        try:
            print("Loading sentiment analyzer...")
            sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            print("Sentiment analyzer loaded!")
        except Exception as e:
            print(f"Failed to load sentiment analyzer: {e}")
            return None
    return sentiment_analyzer

print("Models will be loaded on first use for faster startup!")

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except:
    print("NLTK punkt download failed, will use simple text processing")

# Cache for storing processed data
processed_data_cache = {}

def clean_text(text):
    # Simplified text cleaning
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def get_summary(text):
    try:
        # Create a simple summary using text processing
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return text
        
        # Take first 2-3 sentences as summary
        summary = " ".join(sentences[:3])
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return summary
    except Exception as e:
        print(f"Error in summary generation: {str(e)}")
        return "Unable to generate summary at this time."

# Main routes
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/diary')
def diary():
    return render_template('home.html', questions=questions)

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except:
        return '', 204

@app.route('/start_manual', methods=['POST'])
def start_manual():
    session['answers'] = []
    return redirect(url_for('index', question_id=0))

@app.route('/index', methods=['GET', 'POST'])
def index():
    question_id = int(request.args.get('question_id', 0))
    if question_id >= len(questions):
        return redirect(url_for('summary'))
    return render_template('questions.html', 
                         question=questions[question_id],
                         question_id=question_id,
                         questions=questions)

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        voice_id = data.get('voice_id', VOICE_ID)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return Response(response.content, mimetype='audio/mpeg')
        else:
            print(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Failed to generate speech: {response.text}'}), 500
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        transcription = data.get('transcription', '')
        
        print(f"Submitting answer - Question: {question}, Answer: {answer}")
        
        if not question or not answer:
            return jsonify({'error': 'Missing question or answer'}), 400
        
        # Store in session
        if 'answers' not in session:
            session['answers'] = []
        
        # Clean the answer text before storing
        clean_answer = answer.strip()
        
        # Check if this question already has an answer and update it
        question_exists = False
        for i, existing_answer in enumerate(session['answers']):
            if existing_answer.get('question') == question:
                session['answers'][i] = {
                    'question': question,
                    'answer': clean_answer,
                    'transcription': transcription
                }
                question_exists = True
                print(f"Updated existing answer for question: {question}")
                break
        
        if not question_exists:
            session['answers'].append({
                'question': question,
                'answer': clean_answer,
                'transcription': transcription
            })
            print(f"Added new answer for question: {question}")
        
        # Ensure session is saved
        session.modified = True
        
        print(f"Session now has {len(session['answers'])} answers")
        print(f"Current session answers: {session['answers']}")
        
        return jsonify({'success': True, 'answers_count': len(session['answers'])})
    except Exception as e:
        print(f"Error in submit_answer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/summary')
def summary():
    try:
        # Get all answers from session
        answers = session.get('answers', [])
        print(f"Session answers count: {len(answers)}")
        print(f"Session answers: {answers}")
        
        if not answers:
            print("No answers found in session")
            return render_template('summary.html', 
                                 answers=[],
                                 summary="No diary entry found. Please go back and answer the questions.",
                                 sentiment=None,
                                 advice=None,
                                 current_time=datetime.now())
        
        # Build diary entry from all answers
        diary_entry = ""
        corrected_answers = []
        
        for i, entry in enumerate(answers):
            if entry and 'answer' in entry and entry['answer']:
                original_text = entry['answer'].strip()
                entry['corrected'] = original_text
                diary_entry += f"{original_text}. "
                corrected_answers.append(entry)
                print(f"Added answer {i+1}: {original_text[:50]}...")
        
        print(f"Number of answers processed: {len(corrected_answers)}")
        print(f"Full diary entry length: {len(diary_entry)} characters")
        
        # Generate summary and analysis
        summary_text = generate_summary(diary_entry)
        sentiment = analyze_sentiment(diary_entry)
        advice = generate_advice(diary_entry, sentiment, summary_text)
        
        # Create a datetime object for the template
        current_time = datetime.now()
        
        # Save to database if user is logged in
        if current_user.is_authenticated:
            try:
                diary_entry_obj = DiaryEntry(
                    user_id=current_user.id,
                    answers=corrected_answers,
                    summary=summary_text,
                    sentiment=sentiment,
                    advice=advice
                )
                db.session.add(diary_entry_obj)
                db.session.commit()
                print(f"Diary entry saved to database for user {current_user.username}")
            except Exception as e:
                print(f"Error saving diary entry to database: {str(e)}")
                db.session.rollback()
        
        # Only clear session after successful generation
        session.clear()
        
        return render_template('summary.html', 
                             answers=corrected_answers,
                             summary=summary_text,
                             sentiment=sentiment,
                             advice=advice,
                             current_time=current_time)
    except Exception as e:
        print(f"Error in summary route: {str(e)}")
        return render_template('summary.html', 
                             answers=[],
                             summary="Error generating summary. Please try again.",
                             sentiment=None,
                             advice=None,
                             current_time=datetime.now())

def analyze_sentiment(text):
    try:
        if HUGGINGFACE_API_KEY:
            # Use Hugging Face API for better sentiment analysis
            API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": text})
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    # Get the highest scoring sentiment
                    sentiment_data = result[0]
                    label = sentiment_data['label']
                    score = sentiment_data['score']
                    
                    if label == 'LABEL_0':
                        mood = "Negative"
                    elif label == 'LABEL_1':
                        mood = "Neutral"
                    else:
                        mood = "Positive"
                    
                    return f"Overall mood: {mood} (confidence: {score:.2f})"
        
        # Fallback to TextBlob if no API key or API fails
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        if sentiment > 0.3:
            mood = "Positive"
        elif sentiment < -0.3:
            mood = "Negative"
        else:
            mood = "Neutral"
            
        return f"Overall mood: {mood} (sentiment score: {sentiment:.2f})"
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "Unable to analyze sentiment"

def generate_summary(text):
    """
    Generate a natural, diary-style summary using Cohere API first, then fallback to local processing.
    """
    try:
        if not text or text.strip() == "":
            print("[DEBUG] No text provided to generate_summary.")
            return "You reflected on your day."

        cleaned_text = text.strip()
        cleaned_text = ' '.join(cleaned_text.split())
        print(f"[DEBUG] Diary entry sent to summary: {cleaned_text}")

        # Try Cohere API first (if API key is available)
        print("[DEBUG] Trying Cohere API for summary...")
        cohere_summary = generate_summary_with_cohere(cleaned_text)
        if cohere_summary:
            print("[DEBUG] Using Cohere summary.")
            return cohere_summary

        # Fallback to local summary generator
        print("[DEBUG] Cohere not available, using local summary generator.")
        return generate_local_summary(cleaned_text)

    except Exception as e:
        print(f"[DEBUG] Error in summary generation: {str(e)}")
        return "You reflected on your day."

def generate_advice(text, sentiment, summary=None):
    """
    Generate personalized advice based on the diary entry, sentiment, and Cohere summary.
    """
    try:
        # Try to use Cohere API for advice generation first
        if summary:
            print("[DEBUG] Trying Cohere API for advice generation...")
            cohere_advice = generate_advice_with_cohere(summary, sentiment)
            if cohere_advice:
                print("[DEBUG] Using Cohere advice.")
                return cohere_advice
        
        # Fallback to simple advice generation
        print("Using fallback advice generation")
        
        text_lower = text.lower()
        sentiment_lower = sentiment.lower()
        
        if "positive" in sentiment_lower:
            advice = "Keep up the great energy! Continue focusing on what brings you joy and maintain this positive momentum."
        elif "negative" in sentiment_lower:
            advice = "Remember that difficult days are temporary. Consider talking to someone you trust, practicing self-care, or doing something that usually makes you feel better."
        else:
            advice = "Take time to reflect on your day. Consider what went well and what you might want to improve. Small steps lead to big changes."
        
        return advice
    except Exception as e:
        print(f"Error in advice generation: {str(e)}")
        return "Focus on maintaining a balanced routine and self-care."

# This is the main handler for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

# For local development
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    app.run(debug=True)