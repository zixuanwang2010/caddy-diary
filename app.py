import os
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
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
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

# Configure Flask
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = True
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
        model = whisper.load_model("small", device="cpu")  # Use small model for even better accuracy
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
            summarizer = pipeline("summarization", model="facebook/bart-base-cnn")  # Use base instead of large
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
        # Return a 204 No Content if favicon is not found
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
        voice_id = data.get('voice_id', VOICE_ID)  # Use provided voice_id or default
        
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

@app.route('/debug_session')
def debug_session():
    """Debug route to check session data"""
    answers = session.get('answers', [])
    return jsonify({
        'answers_count': len(answers),
        'answers': answers,
        'session_id': session.get('_id', 'no_id'),
        'session_data': dict(session)
    })

@app.route('/add_test_answers')
def add_test_answers():
    """Add test answers for debugging"""
    if 'answers' not in session:
        session['answers'] = []
    
    test_answers = [
        {'question': 'How are you feeling today?', 'answer': 'I am feeling great today', 'transcription': ''},
        {'question': 'What was the highlight of your day?', 'answer': 'The highlight was meeting my friend', 'transcription': ''},
        {'question': 'What challenges did you face today?', 'answer': 'I faced some work challenges', 'transcription': ''},
        {'question': 'What are you looking forward to tomorrow?', 'answer': 'I am looking forward to the weekend', 'transcription': ''},
        {'question': 'Is there anything you\'d like to improve or change?', 'answer': 'I want to improve my time management', 'transcription': ''}
    ]
    
    session['answers'] = test_answers
    session.modified = True
    
    return jsonify({
        'message': 'Test answers added',
        'answers_count': len(session['answers'])
    })

@app.route('/test_summary')
def test_summary():
    """Test summary generation with sample data"""
    try:
        # Create sample diary entry
        sample_text = "Answer 1: I am feeling great today. Answer 2: The highlight was meeting my friend. Answer 3: I faced some work challenges. Answer 4: I am looking forward to the weekend. Answer 5: I want to improve my time management. "
        
        print(f"Testing summary generation with: {sample_text}")
        
        # Generate summary
        summary_text = generate_summary(sample_text)
        sentiment = analyze_sentiment(sample_text)
        advice = generate_advice(sample_text, sentiment, summary_text)
        
        return jsonify({
            'original_text': sample_text,
            'summary': summary_text,
            'sentiment': sentiment,
            'advice': advice,
            'success': True
        })
    except Exception as e:
        print(f"Error in test_summary: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        })

# Authentication Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            return render_template('signup.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered')
        
        # Create new user (not verified yet)
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create and send verification code
            verification_code = VerificationCode.create_for_user(user.id)
            db.session.add(verification_code)
            db.session.commit()
            
            # Try to send verification email (optional for now)
            try:
                email_service = EmailService()
                if email_service.send_verification_email(email, username, verification_code.code):
                    # Store user ID in session for verification
                    session['pending_verification_user_id'] = user.id
                    session['pending_verification_email'] = email
                    
                    flash('Account created! Please check your email for verification code.', 'success')
                    return redirect(url_for('verify_email'))
                else:
                    # If email fails, still create account but mark as verified
                    user.mark_email_verified()
                    db.session.commit()
                    login_user(user)
                    flash('Account created successfully! Email verification failed, but account is active.', 'warning')
                    return redirect(url_for('dashboard'))
            except Exception as email_error:
                print(f"Email service error: {email_error}")
                # If email service fails, still create account
                user.mark_email_verified()
                db.session.commit()
                login_user(user)
                flash('Account created successfully! Email verification unavailable, but account is active.', 'warning')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            db.session.rollback()
            print(f"Signup error details: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return render_template('signup.html', error=f'Error creating account: {str(e)}')
    
    return render_template('signup.html')

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    user_id = session.get('pending_verification_user_id')
    email = session.get('pending_verification_email')
    
    if not user_id or not email:
        flash('No pending verification found. Please sign up again.', 'error')
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        if 'resend' in request.form:
            # Resend verification code
            try:
                # Create new verification code
                verification_code = VerificationCode.create_for_user(user_id)
                db.session.add(verification_code)
                db.session.commit()
                
                # Send new email
                email_service = EmailService()
                if email_service.send_verification_email(email, User.query.get(user_id).username, verification_code.code):
                    flash('New verification code sent!', 'success')
                else:
                    flash('Error sending verification email. Please try again.', 'error')
            except Exception as e:
                flash('Error resending verification code. Please try again.', 'error')
            
            return render_template('verify_email.html', email=email)
        
        # Verify the code
        verification_code = request.form.get('verification_code')
        
        if not verification_code:
            return render_template('verify_email.html', email=email, error='Please enter the verification code')
        
        # Find the verification code
        code_record = VerificationCode.query.filter_by(
            user_id=user_id, 
            code=verification_code,
            used=False
        ).first()
        
        if not code_record:
            return render_template('verify_email.html', email=email, error='Invalid verification code')
        
        if code_record.is_expired():
            return render_template('verify_email.html', email=email, error='Verification code has expired')
        
        # Mark code as used and verify user
        code_record.mark_used()
        user = User.query.get(user_id)
        user.mark_email_verified()
        
        db.session.commit()
        
        # Clear session and log user in
        session.pop('pending_verification_user_id', None)
        session.pop('pending_verification_email', None)
        
        login_user(user)
        flash('Email verified successfully! Welcome to Caddy Diary!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('verify_email.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Check if email is verified
            if not user.email_verified:
                # Send verification code again
                verification_code = VerificationCode.create_for_user(user.id)
                db.session.add(verification_code)
                db.session.commit()
                
                email_service = EmailService()
                email_service.send_verification_email(user.email, user.username, verification_code.code)
                
                session['pending_verification_user_id'] = user.id
                session['pending_verification_email'] = user.email
                
                flash('Please verify your email first. A new verification code has been sent.', 'error')
                return redirect(url_for('verify_email'))
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Calculate stats
    monthly_entries = len([entry for entry in current_user.diary_entries 
                          if entry.entry_date >= datetime.now().replace(day=1)])
    
    # Calculate current streak
    current_streak = 0
    if current_user.diary_entries:
        entries = sorted(current_user.diary_entries, key=lambda x: x.entry_date, reverse=True)
        current_date = datetime.now().date()
        
        for entry in entries:
            entry_date = entry.entry_date.date()
            if entry_date == current_date:
                current_streak += 1
                current_date -= timedelta(days=1)
            elif entry_date < current_date - timedelta(days=1):
                break
    
    return render_template('dashboard.html', 
                         monthly_entries=monthly_entries,
                         current_streak=current_streak)

@app.route('/entries')
@login_required
def entries():
    # Get all entries sorted by date
    entries = sorted(current_user.diary_entries, key=lambda x: x.entry_date, reverse=True)
    return render_template('entries.html', entries=entries)

@app.route('/view_entry/<int:entry_id>')
@login_required
def view_entry(entry_id):
    entry = DiaryEntry.query.get_or_404(entry_id)
    # Ensure user can only view their own entries
    if entry.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    return render_template('view_entry.html', entry=entry)

@app.route('/phone_call')
def phone_call():
    """Voice call diary entry route"""
    return render_template('phone_call.html')

@app.route('/phone_call', methods=['POST'])
def process_phone_call():
    """Process voice call submission"""
    try:
        # Get the audio file from the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save the audio file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe the audio using Whisper
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(tmp_path)
            transcription = result["text"]
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            # Store transcription in session for the diary entry
            session['voice_transcription'] = transcription
            
            return jsonify({
                'success': True,
                'transcription': transcription,
                'message': 'Voice transcribed successfully!'
            })
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
            
    except Exception as e:
        print(f"Error processing phone call: {str(e)}")
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

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
        
        # Build diary entry from all answers - without grammar correction to avoid corruption
        diary_entry = ""
        corrected_answers = []
        
        for i, entry in enumerate(answers):
            if entry and 'answer' in entry and entry['answer']:
                # Use original text without grammar correction to avoid corruption
                original_text = entry['answer'].strip()
                entry['corrected'] = original_text  # Keep original text
                diary_entry += f"{original_text}. "
                corrected_answers.append(entry)
                print(f"Added answer {i+1}: {original_text[:50]}...")
        
        print(f"Number of answers processed: {len(corrected_answers)}")
        print(f"Full diary entry length: {len(diary_entry)} characters")
        print(f"Full diary entry: '{diary_entry}'")
        
        # Debug: Print each answer individually
        for i, entry in enumerate(corrected_answers):
            print(f"Answer {i+1}: {entry.get('question', 'Unknown question')} - {entry.get('answer', 'No answer')}")
        
        # If we have multiple answers, create a natural diary entry
        if len(corrected_answers) > 1:
            print(f"Processing {len(corrected_answers)} answers for natural summary")
            # Create a natural diary entry that flows like a real diary
            detailed_entry = ""
            for i, entry in enumerate(corrected_answers):
                answer_text = entry['answer'].strip()
                if answer_text:
                    # Create natural flow without rigid structure
                    detailed_entry += f"Answer {i+1}: {answer_text}. "
            diary_entry = detailed_entry
        
        # Ensure we have meaningful content
        if len(diary_entry.strip()) < 10:
            print("Diary entry too short, using fallback")
            diary_entry = "You reflected on your day and shared your thoughts."
        
        # Validate that we have answers for all 5 questions
        expected_questions = 5
        if len(corrected_answers) < expected_questions:
            print(f"Warning: Only {len(corrected_answers)} answers found, expected {expected_questions}")
        elif len(corrected_answers) == expected_questions:
            print(f"Perfect! All {expected_questions} questions have been answered")
        else:
            print(f"Note: {len(corrected_answers)} answers found (more than expected {expected_questions})")
        
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

def transcribe_audio(audio_path):
    try:
        # Ensure the audio file exists
        if not os.path.exists(audio_path):
            return "Error: Audio file not found"
            
        # Get the lazy-loaded model
        whisper_model = get_whisper_model()
        
        # Use optimized settings for better accuracy with base model
        result = whisper_model.transcribe(
            audio_path, 
            fp16=False,  # Disable FP16 for CPU
            language="en",  # Specify language for better accuracy
            task="transcribe",  # Explicitly set task
            verbose=False,  # Reduce logging for speed
            condition_on_previous_text=False,  # Disable for speed
            temperature=0.0,  # Use deterministic output for consistency
            best_of=1,  # Use best of 1 for speed
            beam_size=1  # Use beam size 1 for speed
        )
        return result["text"]
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        return "Error transcribing audio"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400
            
        # Save the audio file temporarily
        temp_path = os.path.join(app.root_path, 'temp_audio.wav')
        audio_file.save(temp_path)
        
        # Try to optimize audio for better transcription
        optimized_path = os.path.join(app.root_path, 'optimized_audio.wav')
        try:
            # Use ffmpeg to optimize audio (mono, 16kHz, normalize)
            subprocess.run([
                'ffmpeg', '-i', temp_path, '-ac', '1', '-ar', '16000', 
                '-af', 'highpass=f=200,lowpass=f=3000,volume=1.5', 
                '-y', optimized_path
            ], check=True, capture_output=True)
            
            # Transcribe the optimized audio
            transcription = transcribe_audio(optimized_path)
            
            # Clean up optimized file
            try:
                os.remove(optimized_path)
            except:
                pass
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to original audio if ffmpeg is not available
            transcription = transcribe_audio(temp_path)
        
        # Clean up the temporary file
        try:
            os.remove(temp_path)
        except:
            pass
            
        return jsonify({'transcription': transcription})
    except Exception as e:
        print(f"Error in transcribe route: {str(e)}")
        return jsonify({'error': str(e)}), 500

def correct_grammar(text):
    try:
        # Use TextBlob for grammar correction (simpler and lighter)
        blob = TextBlob(text)
        corrected = str(blob.correct())
        return corrected
    except Exception as e:
        print(f"Error in grammar correction: {str(e)}")
        return text

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
    Uses the summary to provide more contextual and tailored advice.
    """
    try:
        # Try to use Cohere API for advice generation first (most sophisticated)
        if summary:
            print("[DEBUG] Trying Cohere API for advice generation...")
            cohere_advice = generate_advice_with_cohere(summary, sentiment)
            if cohere_advice:
                print("[DEBUG] Using Cohere advice.")
                return cohere_advice
        
        # Fallback to Hugging Face API for advice generation
        if HUGGINGFACE_API_KEY:
            API_URL = "https://api-inference.huggingface.co/models/gpt2"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            
            # Create a more detailed prompt that includes the summary for better context
            sentiment_mood = "positive" if "positive" in sentiment.lower() else "negative" if "negative" in sentiment.lower() else "neutral"
            
            # Use the summary if available, otherwise use the original text
            context_text = summary if summary else text
            text_preview = context_text[:600] if len(context_text) > 600 else context_text
            
            # Create a more specific prompt that leverages the summary
            if summary:
                prompt = f"Based on this diary summary: '{summary}' and the person's mood being {sentiment_mood}, provide specific, actionable advice in 1-2 sentences that directly addresses what they shared. Make it personal and encouraging."
            else:
                prompt = f"Based on this diary entry: '{text_preview}' and the person's mood being {sentiment_mood}, provide specific, actionable advice in 1-2 sentences that directly addresses what they shared."
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt, "max_length": 150, "temperature": 0.7})
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    advice = result[0]['generated_text']
                    # Clean up the response by removing the prompt
                    advice = advice.replace(prompt, "").strip()
                    # Remove any incomplete sentences at the end
                    if advice.count('.') > 0:
                        sentences = advice.split('.')
                        if len(sentences) > 1:
                            advice = '.'.join(sentences[:-1]) + '.'
                    if advice and len(advice) > 15:  # Ensure we have meaningful advice
                        return advice
        
        # Enhanced fallback that uses the summary for better context
        print("Using enhanced fallback advice generation based on summary and content analysis")
        
        # Use summary for analysis if available, otherwise use original text
        analysis_text = summary if summary else text
        text_lower = analysis_text.lower()
        sentiment_lower = sentiment.lower()
        
        # Extract key themes from the summary/content
        themes = []
        if any(word in text_lower for word in ['work', 'job', 'office', 'meeting', 'project', 'boss', 'colleague', 'deadline', 'professional']):
            themes.append('work')
        if any(word in text_lower for word in ['family', 'friend', 'relationship', 'partner', 'child', 'parent', 'sibling', 'dad', 'mom', 'brother', 'sister']):
            themes.append('relationships')
        if any(word in text_lower for word in ['health', 'exercise', 'sleep', 'diet', 'stress', 'tired', 'energy', 'workout', 'wellbeing']):
            themes.append('health')
        if any(word in text_lower for word in ['study', 'learn', 'school', 'education', 'course', 'exam', 'test', 'assignment', 'math', 'skills']):
            themes.append('education')
        if any(word in text_lower for word in ['money', 'finance', 'budget', 'spending', 'saving', 'bill', 'financial']):
            themes.append('finance')
        if any(word in text_lower for word in ['goal', 'plan', 'future', 'dream', 'aspiration', 'improve']):
            themes.append('goals')
        if any(word in text_lower for word in ['hockey', 'sport', 'game', 'play', 'activity', 'hobby']):
            themes.append('hobbies')
        if any(word in text_lower for word in ['angry', 'upset', 'frustrated', 'disappointed', 'sad', 'hurt']):
            themes.append('conflict')
        
        # Generate advice based on the specific themes found and summary context
        if themes:
            if "positive" in sentiment_lower:
                if 'work' in themes:
                    advice = "Your positive attitude at work is inspiring! Consider documenting your successes and sharing your enthusiasm with your team."
                elif 'relationships' in themes:
                    advice = "These positive relationship moments are precious! Consider expressing your gratitude directly to the people who bring you joy."
                elif 'health' in themes:
                    advice = "Excellent work prioritizing your wellbeing! Keep building these healthy habits and consider how you can inspire others."
                elif 'education' in themes:
                    advice = "Your learning journey is thriving! Consider applying what you're learning in practical ways or teaching others."
                elif 'finance' in themes:
                    advice = "Great job managing your finances! Consider setting up automatic savings or sharing your strategies with others."
                elif 'goals' in themes:
                    advice = "Your goal-setting and progress are impressive! Keep breaking down big goals into manageable steps."
                elif 'hobbies' in themes:
                    advice = "Your passion for your hobbies is wonderful! Consider how you can share this joy with others or use it as a stress reliever."
                else:
                    advice = "Your positive energy is contagious! Keep focusing on what brings you joy and consider how you can share this positivity."
            
            elif "negative" in sentiment_lower:
                if 'work' in themes:
                    advice = "Work challenges can be overwhelming. Consider taking short breaks, prioritizing tasks, or discussing concerns with a trusted colleague."
                elif 'relationships' in themes:
                    if 'conflict' in themes:
                        advice = "Relationship conflicts can be difficult. Consider taking time to cool down, then having an open conversation about what happened."
                    else:
                        advice = "Relationship difficulties are complex. Consider open communication, setting healthy boundaries, or seeking support from a counselor."
                elif 'health' in themes:
                    advice = "Health challenges can be stressful. Start with small, manageable steps and consider consulting a healthcare professional."
                elif 'education' in themes:
                    advice = "Learning obstacles are normal. Break down complex topics into smaller parts and celebrate each step forward."
                elif 'finance' in themes:
                    advice = "Financial stress is common. Consider creating a simple budget or seeking advice from a financial counselor."
                elif 'goals' in themes:
                    advice = "Goal setbacks are temporary. Consider adjusting your timeline or breaking goals into smaller, more achievable steps."
                elif 'conflict' in themes:
                    advice = "Conflicts can be emotionally draining. Consider taking time to process your feelings and finding healthy ways to express them."
                else:
                    advice = "Difficult days are temporary. Consider talking to someone you trust, practicing self-care, or doing something that usually helps."
            
            else:  # neutral sentiment
                if 'work' in themes:
                    advice = "Work life requires balance. Focus on what you can control and celebrate small wins throughout your day."
                elif 'relationships' in themes:
                    advice = "Relationships require ongoing effort. Focus on what you can contribute positively and communicate openly."
                elif 'health' in themes:
                    advice = "Health is a journey, not a destination. Focus on one small improvement you can make today."
                elif 'education' in themes:
                    advice = "Education opens doors. Focus on understanding rather than memorizing, and don't be afraid to ask questions."
                elif 'finance' in themes:
                    advice = "Financial wellness takes time. Focus on small, consistent steps toward your financial goals."
                elif 'goals' in themes:
                    advice = "Goals evolve over time. Consider reviewing and adjusting your plans to better align with your current priorities."
                elif 'hobbies' in themes:
                    advice = "Hobbies are great for balance and joy. Consider how you can make more time for activities that bring you happiness."
                else:
                    advice = "Take time to reflect on your day. Consider what went well and what you might want to improve. Small steps lead to big changes."
        else:
            # General advice based on sentiment
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

@app.route('/elevenlabs/generate-summary-audio', methods=['POST'])
def generate_summary_audio():
    """Generate audio for diary summary"""
    try:
        data = request.get_json()
        summary_text = data.get('summary', '')
        
        if not summary_text:
            return jsonify({'error': 'No summary text provided'}), 400
            
        # Truncate text if too long (ElevenLabs has limits)
        if len(summary_text) > 2500:
            summary_text = summary_text[:2500] + "..."
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": summary_text,
            "model_id": "eleven_monolingual_v1"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return Response(response.content, mimetype='audio/mpeg')
        else:
            print(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Failed to generate summary audio: {response.text}'}), 500
    except Exception as e:
        print(f"Error generating summary audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(debug=True)