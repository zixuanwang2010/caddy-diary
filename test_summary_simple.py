#!/usr/bin/env python3
"""
Simple test for the summary generation function
"""

def generate_summary(text):
    """Generate a simple, natural diary summary from the user's answers"""
    try:
        if not text or text.strip() == "":
            return "You reflected on your day."
        
        # Clean up the text
        cleaned_text = text.strip()
        cleaned_text = ' '.join(cleaned_text.split())
        
        # Check if this is a multi-answer format
        if "Answer 1:" in cleaned_text:
            # Extract answers using simple string splitting
            answers = []
            parts = cleaned_text.split("Answer ")
            
            for part in parts[1:]:  # Skip the first empty part
                if ":" in part:
                    answer_text = part.split(":", 1)[1].strip()
                    # Remove trailing period and clean up
                    if answer_text.endswith("."):
                        answer_text = answer_text[:-1].strip()
                    if answer_text:
                        answers.append(answer_text)
            
            print(f"Extracted {len(answers)} answers: {answers}")
            
            # Clean up answers to remove redundant phrases
            def clean_answer(answer):
                """Clean up an answer to remove redundant phrases"""
                # Remove common redundant phrases
                answer = answer.replace("I am feeling ", "").replace("I'm feeling ", "")
                answer = answer.replace("The highlight was ", "").replace("highlight was ", "")
                answer = answer.replace("I faced some ", "").replace("faced some ", "")
                answer = answer.replace("I am looking forward to ", "").replace("looking forward to ", "")
                answer = answer.replace("I want to improve ", "").replace("want to improve ", "")
                return answer.strip()
            
            # Clean up all answers
            cleaned_answers = [clean_answer(answer) for answer in answers]
            print(f"Cleaned answers: {cleaned_answers}")
            
            # Create natural summary based on number of answers
            if len(cleaned_answers) == 5:
                feeling, highlight, challenges, looking_forward, improvements = cleaned_answers
                summary = f"Today you're feeling {feeling}. The highlight of your day was {highlight}. You faced some challenges with {challenges}, but you're looking forward to {looking_forward}. You'd like to improve {improvements}."
            elif len(cleaned_answers) >= 3:
                summary = f"Today you shared your thoughts. {'. '.join(cleaned_answers)}."
            elif len(cleaned_answers) == 2:
                summary = f"Today you reflected on {cleaned_answers[0]} and {cleaned_answers[1]}."
            elif len(cleaned_answers) == 1:
                summary = f"Today you shared that {cleaned_answers[0]}."
            else:
                summary = "Today you reflected on your day."
        else:
            # For freeform text, create a simple summary
            if len(cleaned_text) < 50:
                summary = f"Today you shared that {cleaned_text}."
            else:
                summary = f"Today you reflected on your day, sharing that {cleaned_text[:200]}..."
        
        return summary
        
    except Exception as e:
        print(f"Error in summary generation: {str(e)}")
        return "Today you reflected on your day."

# Test the function
if __name__ == "__main__":
    print("Testing summary generation...")
    
    # Test 1: Full 5 answers
    test1 = "Answer 1: I am feeling great today. Answer 2: The highlight was meeting my friend. Answer 3: I faced some work challenges. Answer 4: I am looking forward to the weekend. Answer 5: I want to improve my time management."
    result1 = generate_summary(test1)
    print(f"\nTest 1 (5 answers): {result1}")
    
    # Test 2: Single answer
    test2 = "Answer 1: My athleticism."
    result2 = generate_summary(test2)
    print(f"\nTest 2 (1 answer): {result2}")
    
    # Test 3: Freeform text
    test3 = "I had a good day today and learned a lot."
    result3 = generate_summary(test3)
    print(f"\nTest 3 (freeform): {result3}")
    
    print("\nSummary generation test completed!") 