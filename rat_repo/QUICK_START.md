# Rat Assistant - Quick Start Guide

## What You Just Built

An LLM-powered conversational agent with an **animated rat avatar** that expresses emotions through movement!

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌────────────────────────────────────────────────────────┐
│  DRIVER AGENT (GPT-4o-mini)                            │
│  • Maintains conversation context                      │
│  • Generates intelligent responses                     │
└────────────────────┬───────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────────┐    ┌─────────────────────┐
│ ANIMATION        │    │ MESSAGE             │
│ SUBAGENT         │    │ SUBAGENT            │
│                  │    │                     │
│ • Analyzes       │    │ • Refines text      │
│   emotion        │    │ • Formats output    │
│ • Creates        │    │                     │
│   animations     │    │                     │
└────────┬─────────┘    └──────────┬──────────┘
         ↓                         ↓
    RAT                DISPLAYED
    ANIMATION           MESSAGE
```

## 🚀 Getting Started

### 1. Set Your OpenAI API Key

```powershell
# PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

### 2. Run the System

```bash
# With animated rat window
python main.py

# Console-only mode (for testing without graphics)
python main.py --console-only
```

### 3. Chat with Your Rat!

```
You: Hello! How are you today?

[Processing...]

Rat Assistant [happy]: Hello there! I'm doing wonderfully, 
thank you for asking! How can I help you today?

*bobs head happily*
```

## 📁 Files Created

### Core LLM System (`llm/`)
- **`config.py`** - Configuration and API settings
- **`driver_agent.py`** - Main conversational AI agent
- **`animation_subagent.py`** - Emotion analyzer & animation controller
- **`message_subagent.py`** - Message processor
- **`orchestrator.py`** - Main coordinator (runs the show!)

### Entry Points
- **`main.py`** - Run this to start the assistant
- **`verify_setup.py`** - Check if everything is installed correctly

### Documentation
- **`PROJECT_README.md`** - Complete project documentation
- **`llm/README.md`** - Detailed LLM architecture guide
- **`.env.example`** - Environment configuration template

## 🎭 Emotion System

The rat automatically expresses emotions based on conversation:

| **What It Says** | **How It Moves** | **Emotion** |
|------------------|------------------|-------------|
| "That's amazing!" | Happy bob | 😊 Happy |
| "Let me think..." | Upward gaze | 🤔 Thinking |
| "I'm so excited!" | Wiggle dance | 🎉 Excited |
| "Really? Wow!" | Pull back | 😲 Surprised |
| "Hmm, interesting..." | Head tilt | 🧐 Curious |
| "I'm sorry to hear..." | Downward look | 😢 Sad |

## 🎮 Usage Examples

### Interactive Conversation

```bash
python main.py
```

### Test Individual Components

```bash
# Test all agents
python -m llm.example_usage

# Verify installation
python verify_setup.py
```

### Programmatic Usage

```python
from llm import AgentOrchestrator, AgentConfig

# Create your rat assistant
orchestrator = AgentOrchestrator()

# Process a message
result = orchestrator.process_user_input("Tell me about rats!")

print(result['message'])     # Assistant's response
print(result['emotion'])     # Detected emotion
```

## 🎨 Customization

### Change the Rat's Personality

Edit [`llm/config.py`](llm/config.py):

```python
driver_system_prompt: str = """You are a [YOUR PERSONALITY HERE] rat assistant..."""
```

### Add New Emotions

Edit [`llm/animation_subagent.py`](llm/animation_subagent.py):

```python
@staticmethod
def _create_my_emotion_animation() -> BehaviorScript:
    script = BehaviorScript("my_emotion")
    script.rotate(x=20, z=10, duration=0.5, easing="ease_out")
    return script

# Register it:
ANIMATION_BEHAVIORS["my_emotion"] = {
    "script": lambda: AnimationSubagent._create_my_emotion_animation(),
    "description": "My custom emotion"
}
```

### Adjust Response Creativity

```powershell
$env:LLM_TEMPERATURE = "0.9"  # More creative responses
```

## 🔧 Troubleshooting

### "No OPENAI_API_KEY found"
```powershell
$env:OPENAI_API_KEY = "your-key-here"
```

### Animation window doesn't appear
```bash
# Try console-only mode first
python main.py --console-only
```

### ImportError: No module named 'openai'
```bash
pip install openai
```

### Want to test without using API credits?
Use console-only mode and limit testing, or use a cheaper model like gpt-3.5-turbo.

## 🎯 Next Steps

1. **Add Speech Input**: Integrate speech-to-text (mentioned in your requirements)
2. **Add Voice Output**: Text-to-speech for rat responses
3. **Web Interface**: Create a web UI instead of console
4. **More Animations**: Add compound emotions (happily curious, sadly concerned, etc.)
5. **Personality Modes**: Let users choose different rat personalities

## 📚 Learn More

- [Full Project Documentation](PROJECT_README.md)
- [LLM Architecture Details](llm/README.md)
- [Animation System Guide](animation/README.md)

## 💡 Pro Tips

- Start with `--console-only` to test conversation flow
- Set `LLM_TEMPERATURE=0.3` for more consistent responses
- Use `gpt-3.5-turbo` instead of `gpt-4o-mini` for faster/cheaper responses
- The animation window can be closed with ESC

---

**Have fun chatting with your rat!**

*Created for hackathon - Feel free to extend and customize!*
