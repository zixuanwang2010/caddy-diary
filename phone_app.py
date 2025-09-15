from flask import Flask, render_template, request, jsonify, session
from phone_call import start_call_test
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use the same secret key as the main app for session sharing
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

@app.route('/')
def start():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Start Your Diary</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #4F46E5;
            --secondary-color: #818CF8;
            --background-color: #F3F4F6;
            --text-color: #1F2937;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 600px;
            width: 90%;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .title {
            color: var(--primary-color);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .subtitle {
            color: var(--text-color);
            font-size: 1.1rem;
            margin-bottom: 2rem;
            text-align: center;
            line-height: 1.6;
        }
        
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .start-button {
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            font-weight: 500;
            width: 100%;
            text-align: center;
            transition: all 0.2s;
            cursor: pointer;
            border: none;
            font-size: 1.1rem;
            text-decoration: none;
            display: inline-block;
        }
        
        .manual-button {
            background-color: var(--primary-color);
            color: white;
        }
        
        .manual-button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-1px);
        }
        
        .phone-button {
            background-color: #10b981;
            color: white;
        }
        
        .phone-button:hover {
            background-color: #059669;
            transform: translateY(-1px);
        }
        
        .start-button:active {
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm border-b border-gray-200 mb-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <a href="http://localhost:5000" class="flex items-center text-gray-900 hover:text-indigo-600 transition-colors">
                        <i class="fas fa-book-open text-2xl text-indigo-600 mr-3"></i>
                        <span class="text-xl font-bold">Caddy Diary</span>
                    </a>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="http://localhost:5000" class="text-gray-600 hover:text-indigo-600 transition-colors text-sm">
                        <i class="fas fa-home mr-1"></i>
                        Back to Home
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="card">
            <h1 class="title">Welcome to Your Digital Diary</h1>
            <p class="subtitle">
                Choose how you'd like to start your daily reflection journey. You can type your thoughts manually or use phone call recording.
            </p>
            <div class="button-container">
                <a href="http://localhost:5000" class="start-button manual-button">
                    📝 Manual Entry (Type in Voice Input)
                </a>
                <form action="/start_call" method="post" style="margin: 0;">
                    <button type="submit" class="start-button phone-button">
                        📞 Phone Call Recording
                    </button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/start_call', methods=['POST'])
def start_call():
    try:
        # Accept form data (not JSON)
        phone_number = request.form.get('phone_number', None)
        # If you want to prompt for a phone number, you can add an input to start.html
        if not phone_number:
            # For demo, use a placeholder or handle as needed
            phone_number = '0000000000'
        
        # Get diary content from session if available
        diary_content = None
        if 'answers' in session:
            answers = session.get('answers', [])
            if answers:
                # Build diary entry from answers
                diary_entry = ""
                for entry in answers:
                    if entry and 'answer' in entry and entry['answer']:
                        diary_entry += f"{entry['answer']} "
                diary_content = diary_entry.strip()
        
        print(f"Received call request for phone number: {phone_number}")
        print(f"Diary content: {diary_content[:100] if diary_content else 'None'}...")
        
        result = start_call_test(phone_number, diary_content)
        
        print(f"Call result: {result}")
        
        if result.get('success'):
            return render_template('call_result.html', 
                success=True,
                message=result.get('message', 'Call initiated successfully'),
                call_id=result.get('call_id'),
                details='Check your phone for the incoming call'
            )
        else:
            error_msg = result.get('error', 'Unknown error occurred')
            return render_template('call_result.html',
                success=False,
                error=error_msg,
                details='Please check your API key and try again'
            )
    except Exception as e:
        print(f"Exception in start_call route: {str(e)}")
        return render_template('call_result.html',
            success=False,
            error=str(e),
            details='An unexpected error occurred'
        )

if __name__ == '__main__':
    app.run(debug=True, port=5001) 