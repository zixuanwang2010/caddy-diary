#!/usr/bin/env python3
"""
Test script to show multiple examples of the improved summary generator
"""

from local_summary import generate_local_summary

def test_multiple_examples():
    """Test the summary generator with different examples"""
    
    examples = [
        {
            "input": "Answer 1: Today I am feeling great. Answer 2: The highlight of my day was doing Clip and Climb with my friends. Answer 3: The challenges I faced today was climbing the Beanstalk wall in Clip and Climb. Answer 4: I am looking forward to work experience. Answer 5: I would like to improve my strength and fitness.",
            "description": "Example 1: Physical activity and goals"
        },
        {
            "input": "Answer 1: Today I am feeling tired but accomplished. Answer 2: The highlight of my day was finishing my big project at work. Answer 3: The challenges I faced today was dealing with difficult coworkers. Answer 4: I am looking forward to the weekend. Answer 5: I would like to improve my communication skills.",
            "description": "Example 2: Work-related experiences"
        },
        {
            "input": "Answer 1: Today I am feeling happy and grateful. Answer 2: The highlight of my day was spending time with my family. Answer 3: The challenges I faced today was managing my time between work and family. Answer 4: I am looking forward to my vacation next month. Answer 5: I would like to improve my work-life balance.",
            "description": "Example 3: Family and balance"
        }
    ]
    
    print("🧪 Testing Improved Summary Generator with Multiple Examples")
    print("=" * 70)
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 {example['description']}")
        print("-" * 50)
        print(f"Input: {example['input']}")
        print()
        
        summary = generate_local_summary(example['input'])
        print(f"✅ Summary: {summary}")
        print()

if __name__ == "__main__":
    test_multiple_examples() 