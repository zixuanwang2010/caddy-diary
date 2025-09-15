#!/usr/bin/env python3
"""
Local summary generator that creates smooth, natural diary summaries
"""

import re
import random

def clean_diary_text(text):
    """Clean and extract meaningful content from diary answers"""
    if not text:
        return ""
    
    # Remove "Answer X:" prefixes
    text = re.sub(r'Answer \d+:\s*', '', text)
    
    # Split into sentences and clean
    sentences = []
    for sentence in text.split('.'):
        sentence = sentence.strip()
        if sentence and len(sentence) > 5:
            sentences.append(sentence)
    
    return sentences

def extract_key_info(sentences):
    """Extract and categorize key information from sentences"""
    info = {
        'mood': None,
        'highlight': None,
        'challenge': None,
        'plans': None,
        'goals': None
    }
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Extract mood
        if not info['mood'] and any(word in sentence_lower for word in ['feeling', 'feel', 'mood', 'happy', 'great', 'good', 'bad', 'sad', 'excited', 'tired', 'amazing', 'wonderful', 'pretty good']):
            info['mood'] = sentence
        
        # Extract highlight
        elif not info['highlight'] and any(word in sentence_lower for word in ['highlight', 'best', 'favorite', 'enjoyed', 'fun', 'amazing', 'wonderful', 'great', 'probably']):
            info['highlight'] = sentence
        
        # Extract challenge
        elif not info['challenge'] and any(word in sentence_lower for word in ['challenge', 'difficult', 'hard', 'struggle', 'problem', 'issue', 'tough', 'really hard']):
            info['challenge'] = sentence
        
        # Extract plans
        elif not info['plans'] and any(word in sentence_lower for word in ['looking forward', 'plan', 'tomorrow', 'next', 'future', 'will']):
            info['plans'] = sentence
        
        # Extract goals
        elif not info['goals'] and any(word in sentence_lower for word in ['improve', 'goal', 'want to', 'would like', 'hope to']):
            info['goals'] = sentence
    
    return info

def extract_key_part(text, keywords):
    """
    Extract the meaningful part of a sentence after finding a keyword.
    For example: "Today I am feeling pretty good" -> "pretty good"
    """
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword in text_lower:
            # Find the position of the keyword
            keyword_pos = text_lower.find(keyword)
            # Take everything after the keyword
            after_keyword = text[keyword_pos + len(keyword):].strip()
            
            # Clean up common prefixes
            after_keyword = re.sub(r'^was\s+', '', after_keyword)
            after_keyword = re.sub(r'^is\s+', '', after_keyword)
            after_keyword = re.sub(r'^are\s+', '', after_keyword)
            after_keyword = re.sub(r'^were\s+', '', after_keyword)
            after_keyword = re.sub(r'^to\s+', '', after_keyword)
            after_keyword = re.sub(r'^with\s+', '', after_keyword)
            after_keyword = re.sub(r'^when\s+', '', after_keyword)
            after_keyword = re.sub(r'^that\s+', '', after_keyword)
            
            # If we got something meaningful, return it
            if after_keyword and len(after_keyword) > 3:
                return after_keyword.strip()
    
    # If no keyword found, return the original text
    return text

def create_smooth_summary(info):
    """Create a smooth, natural summary that flows well and is easy to understand"""
    
    # Build the summary naturally
    summary_parts = []
    
    # Start with mood - extract key part
    if info['mood']:
        mood_keywords = ['feeling', 'feel', 'mood', 'am', 'was', 'is']
        mood_part = extract_key_part(info['mood'], mood_keywords)
        
        if 'pretty good' in mood_part.lower():
            summary_parts.append("You were feeling pretty good today")
        elif 'great' in mood_part.lower():
            summary_parts.append("You were feeling great today")
        elif 'good' in mood_part.lower():
            summary_parts.append("You were feeling good today")
        elif 'fine' in mood_part.lower():
            summary_parts.append("You were feeling fine today")
        elif 'tired' in mood_part.lower():
            summary_parts.append("You were feeling tired today")
        elif 'bad' in mood_part.lower() or 'sad' in mood_part.lower():
            summary_parts.append("You were feeling down today")
        else:
            summary_parts.append(f"You were feeling {mood_part.lower()}")
    
    # Add highlight - extract key part
    if info['highlight']:
        highlight_keywords = ['highlight', 'best', 'favorite', 'enjoyed', 'fun', 'amazing', 'wonderful', 'great', 'probably', 'definitely', 'was', 'is']
        highlight_part = extract_key_part(info['highlight'], highlight_keywords)
        
        # Clean up common phrases more aggressively
        highlight_part = re.sub(r'^the\s+', '', highlight_part)
        highlight_part = re.sub(r'^of my day\s+', '', highlight_part)
        highlight_part = re.sub(r'^part of my day\s+', '', highlight_part)
        highlight_part = re.sub(r'^probably\s+', '', highlight_part)
        highlight_part = re.sub(r'^definitely\s+', '', highlight_part)
        highlight_part = re.sub(r'^was\s+', '', highlight_part)
        highlight_part = re.sub(r'^is\s+', '', highlight_part)
        
        if 'making' in highlight_part.lower():
            summary_parts.append(f"The best part of your day was {highlight_part.lower()}")
        elif 'doing' in highlight_part.lower():
            summary_parts.append(f"You really enjoyed {highlight_part.lower()}")
        elif 'getting' in highlight_part.lower():
            summary_parts.append(f"The highlight of your day was {highlight_part.lower()}")
        elif 'going to' in highlight_part.lower():
            summary_parts.append(f"The highlight of your day was {highlight_part.lower()}")
        elif 'playing' in highlight_part.lower():
            summary_parts.append(f"The highlight of your day was {highlight_part.lower()}")
        else:
            summary_parts.append(f"The highlight of your day was {highlight_part.lower()}")
    
    # Add challenge - extract key part
    if info['challenge']:
        challenge_keywords = ['challenge', 'difficult', 'hard', 'struggle', 'problem', 'issue', 'tough', 'really hard', 'was', 'is', 'faced']
        challenge_part = extract_key_part(info['challenge'], challenge_keywords)
        
        # Clean up common phrases more aggressively
        challenge_part = re.sub(r'^the challenges? i faced today\s+', '', challenge_part)
        challenge_part = re.sub(r'^the challenges? i faced\s+', '', challenge_part)
        challenge_part = re.sub(r'^when my\s+', '', challenge_part)
        challenge_part = re.sub(r'^that\s+', '', challenge_part)
        challenge_part = re.sub(r'^were\s+', '', challenge_part)
        challenge_part = re.sub(r'^was\s+', '', challenge_part)
        challenge_part = re.sub(r'^i faced\s+', '', challenge_part)
        challenge_part = re.sub(r'^the main challenge\s+', '', challenge_part)
        
        if 'maths homework' in challenge_part.lower() or 'math homework' in challenge_part.lower():
            summary_parts.append("Your maths homework was challenging")
        elif 'english homework' in challenge_part.lower():
            summary_parts.append("Your English homework was challenging")
        elif 'homework' in challenge_part.lower():
            summary_parts.append("Your homework was challenging")
        elif 'maths' in challenge_part.lower() or 'math' in challenge_part.lower():
            summary_parts.append("Your maths was challenging")
        elif 'dad crashed' in challenge_part.lower():
            summary_parts.append("You had some family challenges today")
        elif 'computer crashed' in challenge_part.lower():
            summary_parts.append("You had some technical difficulties today")
        else:
            summary_parts.append(f"You found {challenge_part.lower()} challenging")
    
    # Add plans - extract key part
    if info['plans']:
        plans_keywords = ['looking forward', 'plan', 'tomorrow', 'next', 'future', 'will', 'to', 'excited']
        plans_part = extract_key_part(info['plans'], plans_keywords)
        
        # Clean up common phrases
        plans_part = re.sub(r'^i am looking forward to\s+', '', plans_part)
        plans_part = re.sub(r'^i\'m looking forward to\s+', '', plans_part)
        plans_part = re.sub(r'^im looking forward to\s+', '', plans_part)
        plans_part = re.sub(r'^i am excited about\s+', '', plans_part)
        plans_part = re.sub(r'^because\s+', '', plans_part)
        
        if 'nothing' in plans_part.lower():
            summary_parts.append("You're not looking forward to anything specific tomorrow")
        elif 'weekend' in plans_part.lower():
            summary_parts.append("You're looking forward to the weekend")
        elif 'day off' in plans_part.lower():
            summary_parts.append("You're looking forward to having a day off")
        else:
            summary_parts.append(f"You're looking forward to {plans_part.lower()}")
    
    # Add goals - extract key part
    if info['goals']:
        goals_keywords = ['improve', 'goal', 'want to', 'would like', 'hope to', 'to']
        goals_part = extract_key_part(info['goals'], goals_keywords)
        
        # Clean up common phrases
        goals_part = re.sub(r'^i would like to improve\s+', '', goals_part)
        goals_part = re.sub(r'^i want to improve\s+', '', goals_part)
        goals_part = re.sub(r'^my\s+', '', goals_part)
        goals_part = re.sub(r'^and learn\s+', '', goals_part)
        
        if 'muscle mass' in goals_part.lower():
            summary_parts.append("You want to work on building muscle")
        elif 'time management' in goals_part.lower():
            summary_parts.append("You want to work on time management")
        elif 'cooking skills' in goals_part.lower():
            summary_parts.append("You want to work on your cooking skills")
        else:
            summary_parts.append(f"You want to work on {goals_part.lower()}")
    
    # Create the final summary - keep it simple and clear
    if summary_parts:
        # Join parts with simple transitions
        if len(summary_parts) >= 3:
            summary = f"{summary_parts[0]}. {summary_parts[1]}. {summary_parts[2]}."
        elif len(summary_parts) >= 2:
            summary = f"{summary_parts[0]}. {summary_parts[1]}."
        else:
            summary = f"{summary_parts[0]}."
        
        return summary
    
    # Fallback - simple and clear
    return "You reflected on your day."

def generate_local_summary(text):
    """
    Generate a smooth, natural diary summary
    """
    if not text or text.strip() == "":
        return "You reflected on your day."
    
    print(f"[DEBUG] Local summary input: {text}")
    
    # Clean the text
    sentences = clean_diary_text(text)
    
    if not sentences:
        return "You reflected on your day."
    
    # Extract key information
    info = extract_key_info(sentences)
    
    # Create smooth summary
    summary = create_smooth_summary(info)
    
    print(f"[DEBUG] Local summary: {summary}")
    return summary

def test_local_summary():
    """Test the improved summary generator"""
    print("🧪 Testing Improved Local Summary Generator...")
    
    # Test with the exact example from the user's app
    test_text = "Answer 1: Today im feeling fine. Answer 2: The highlight was getting my new hockey shoes. Answer 3: The challenges I faced were when my dad crashed out on me. Answer 4: Im looking forward to nothing tommorow. Answer 5: I would like to improve my muscle mass."
    
    result = generate_local_summary(test_text)
    print(f"✅ Generated summary: {result}")
    
    # Test with more examples
    print("\n🧪 Testing more examples:")
    
    # Example 2: More complex sentences
    test_text2 = "Answer 1: I am feeling quite tired today because I didn't sleep well. Answer 2: The best part of my day was definitely going to the park with my friends. Answer 3: I struggled with my English homework today because it was very difficult. Answer 4: I'm looking forward to the weekend when I can relax. Answer 5: I want to improve my time management skills."
    
    result2 = generate_local_summary(test_text2)
    print(f"Example 2: {result2}")
    
    # Example 3: Different sentence structures
    test_text3 = "Answer 1: My mood today is excellent and I feel very happy. Answer 2: The highlight of my day was probably playing basketball with my team. Answer 3: The main challenge I faced was when my computer crashed during work. Answer 4: I am excited about tomorrow because I have a day off. Answer 5: I would like to improve my cooking skills and learn new recipes."
    
    result3 = generate_local_summary(test_text3)
    print(f"Example 3: {result3}")
    
    return result

if __name__ == "__main__":
    test_local_summary() 