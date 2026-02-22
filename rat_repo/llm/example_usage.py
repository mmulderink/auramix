"""
Example usage of the LLM agent system without running the full orchestrator.
Demonstrates how to use individual agents programmatically.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.config import AgentConfig
from llm.driver_agent import DriverAgent
from llm.animation_subagent import AnimationSubagent
from llm.message_subagent import MessageSubagent


def demo_driver_agent():
    """Demonstrate the driver agent alone."""
    print("\n" + "="*60)
    print("DEMO: Driver Agent")
    print("="*60)
    
    config = AgentConfig.from_env()
    driver = DriverAgent(config)
    
    # Test conversation
    test_inputs = [
        "Hello! How are you?",
        "What's your favorite thing about being a rat?",
        "Can you tell me a fun fact?"
    ]
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        response = driver.process_input(user_input)
        print(f"Driver: {response}")
    
    print("\n" + "="*60)


def demo_animation_analysis():
    """Demonstrate the animation subagent's emotion analysis."""
    print("\n" + "="*60)
    print("DEMO: Animation Emotion Analysis")
    print("="*60)
    
    config = AgentConfig.from_env()
    animator = AnimationSubagent(config)
    
    test_messages = [
        "That's amazing! I'm so excited to hear that!",
        "Hmm, let me think about that for a moment...",
        "I'm really sorry to hear that happened.",
        "Wait, what? That's surprising!",
        "Yes, I completely agree with you on that."
    ]
    
    for message in test_messages:
        print(f"\nMessage: {message}")
        script, analysis = animator.analyze_and_animate(message)
        print(f"  Emotion: {analysis.get('emotion', 'unknown')}")
        print(f"  Intensity: {analysis.get('intensity', 'unknown')}")
        print(f"  Animation: {analysis.get('animation', 'unknown')}")
        print(f"  Script commands: {len(script.commands)}")
    
    print("\n" + "="*60)


def demo_message_processing():
    """Demonstrate message refinement."""
    print("\n" + "="*60)
    print("DEMO: Message Processing")
    print("="*60)
    
    config = AgentConfig.from_env()
    processor = MessageSubagent(config)
    
    raw_message = "well uh yeah so basically what I'm trying to say is that rats are pretty cool animals and stuff"
    
    print(f"\nRaw message: {raw_message}")
    refined = processor.process_message(raw_message)
    print(f"Refined: {refined}")
    
    # Test console formatting
    long_message = "This is a really long message that needs to be wrapped properly for console display so it doesn't go off the edge of the screen and look ugly."
    print(f"\n\nOriginal: {long_message}")
    print("\nFormatted (max width 40):")
    print(processor.format_for_console(long_message, max_width=40))
    
    print("\n" + "="*60)


def demo_full_pipeline():
    """Demonstrate the full agent pipeline."""
    print("\n" + "="*60)
    print("DEMO: Full Agent Pipeline")
    print("="*60)
    
    config = AgentConfig.from_env()
    driver = DriverAgent(config)
    animator = AnimationSubagent(config)
    processor = MessageSubagent(config)
    
    user_input = "Hello! Can you explain what makes rats such clever animals?"
    
    print(f"\nUser: {user_input}")
    print("\n[Pipeline Processing...]")
    
    # Step 1: Driver generates response
    print("\n1. Driver Agent processing...")
    driver_response = driver.process_input(user_input)
    print(f"   Response: {driver_response[:100]}...")
    
    # Step 2: Animation analysis
    print("\n2. Animation Subagent analyzing emotion...")
    script, analysis = animator.analyze_and_animate(driver_response)
    print(f"   Detected emotion: {analysis.get('emotion', 'unknown')}")
    print(f"   Animation: {analysis.get('animation', 'unknown')}")
    
    # Step 3: Message refinement (optional)
    print("\n3. Message Subagent refining...")
    final_message = processor.process_message(driver_response)
    print(f"   Final: {final_message[:100]}...")
    
    print("\n[Complete!]")
    print("\n" + "="*60)


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "LLM AGENT SYSTEM - EXAMPLES" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            print("\n⚠️  WARNING: No OPENAI_API_KEY found in environment!")
            print("   Set it with: $env:OPENAI_API_KEY = 'your-key-here'")
            print("   Demos will fail without a valid API key.\n")
            return
        
        # Run demos
        demo_driver_agent()
        input("\nPress Enter to continue to next demo...")
        
        demo_animation_analysis()
        input("\nPress Enter to continue to next demo...")
        
        demo_message_processing()
        input("\nPress Enter to continue to next demo...")
        
        demo_full_pipeline()
        
        print("\n✅ All demos complete!")
        print("\nTo run the full interactive system, use: python main.py")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
