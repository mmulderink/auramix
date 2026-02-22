"""
Quick verification script to test the LLM agent system setup.
Run this to verify all components are properly installed and configured.
"""

import sys
import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    
    packages = {
        'numpy': 'numpy',
        'moderngl': 'moderngl',
        'moderngl_window': 'moderngl_window',
        'openai': 'openai'
    }
    
    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NOT FOUND")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def check_api_key():
    """Check if OpenAI API key is configured."""
    print("\nChecking API configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"  ✓ OPENAI_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("  ✗ OPENAI_API_KEY not found in environment")
        print("\n⚠️  Set your API key with:")
        print("     $env:OPENAI_API_KEY = 'your-key-here'  # PowerShell")
        return False


def check_imports():
    """Check if LLM modules can be imported."""
    print("\nChecking LLM module imports...")
    
    try:
        from llm import AgentConfig, DriverAgent, AnimationSubagent, MessageSubagent, AgentOrchestrator
        print("  ✓ All LLM modules import successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def check_animation_system():
    """Check if animation system can be imported."""
    print("\nChecking animation system...")
    
    try:
        from animation.rat_model import RatModel
        from animation.animation_system import AnimationSystem
        from animation.behavior_script import BehaviorScript
        print("  ✓ Animation system imports successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def run_basic_test():
    """Run a basic functionality test."""
    print("\nRunning basic functionality test...")
    
    try:
        # Check if we can create a config
        from llm import AgentConfig
        config = AgentConfig(api_key="test-key")
        print("  ✓ AgentConfig creation works")
        
        # Check if we can create a rat model
        from animation.rat_model import RatModel
        rat = RatModel("test")
        print(f"  ✓ RatModel creation works (vertices: {len(rat.bind_vertices)})")
        
        # Check if we can create a behavior script
        from animation.behavior_script import BehaviorScript
        script = BehaviorScript("test")
        script.rotate(x=10, duration=1.0)
        print(f"  ✓ BehaviorScript creation works (commands: {len(script.commands)})")
        
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("LLM AGENT SYSTEM - VERIFICATION")
    print("="*60 + "\n")
    
    results = []
    
    # Run all checks
    results.append(("Dependencies", check_dependencies()))
    results.append(("API Key", check_api_key()))
    results.append(("LLM Imports", check_imports()))
    results.append(("Animation System", check_animation_system()))
    results.append(("Basic Tests", run_basic_test()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ System is ready to use!")
        print("\nRun the assistant with:")
        print("  python main.py                    # With animation")
        print("  python main.py --console-only     # Console only")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
