# Rat Assistant - LLM Agentic Architecture

An intelligent conversational AI system with an animated rat avatar. This project combines a multi-agent LLM architecture with a 3D animation system to create an engaging, emotionally expressive assistant.

## 🎯 Overview

This system consists of two main components:

1. **Animation System** (`animation/`) - 3D procedural animation with ModernGL rendering
2. **LLM Agent Architecture** (`llm/`) - Multi-agent conversational AI with emotion-driven animations

## 🏗️ Architecture

### Multi-Agent System

```
User Input
    ↓
┌─────────────────────┐
│   Driver Agent      │  ← Main conversational AI
│   (GPT-4o-mini)     │
└──────────┬──────────┘
           │ Response
           ↓
    ┌──────┴──────┐
    │             │
    ↓             ↓
┌─────────────┐ ┌──────────────────┐
│  Animation  │ │  Message         │
│  Subagent   │ │  Subagent        │
│             │ │                  │
│ Analyzes    │ │ Refines message  │
│ emotion &   │ │ for display      │
│ generates   │ │                  │
│ animations  │ │                  │
└──────┬──────┘ └────────┬─────────┘
       │                 │
       ↓                 ↓
   Animation         Final Message
   Playback          Display
```

### Components

- **Driver Agent**: Core conversational AI that maintains context and generates responses
- **Animation Subagent**: Analyzes emotional content and creates animation behavior scripts
- **Message Subagent**: Refines and formats messages for optimal readability
- **Orchestrator**: Coordinates all agents and manages the animation display

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"
```

### 3. Run the Assistant

```bash
# With animation window
python main.py

# Console-only mode (no graphics)
python main.py --console-only
```

## 📁 Project Structure

```
hackathon/
├── animation/              # 3D Animation System
│   ├── animation_system.py # Core animation engine
│   ├── rat_model.py      # 3D rat head model
│   ├── renderer_gl.py     # ModernGL renderer
│   ├── behavior_script.py # Animation scripting
│   └── rigging.py         # Bone rigging system
│
├── llm/                   # LLM Agent Architecture
│   ├── config.py          # Configuration & API settings
│   ├── driver_agent.py    # Main conversational agent
│   ├── animation_subagent.py  # Animation controller
│   ├── message_subagent.py    # Message processor
│   ├── orchestrator.py    # Main coordinator
│   ├── example_usage.py   # Demo scripts
│   └── README.md          # LLM system documentation
│
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── .env.example          # Environment configuration template
```

## 🎭 Emotion-Driven Animations

The system automatically detects emotions in responses and triggers appropriate animations:

| Emotion | Animation | Description |
|---------|-----------|-------------|
| Happy | Upward bob | Joyful head movement |
| Excited | Wiggle | Enthusiastic side-to-side |
| Curious | Tilt | Inquisitive head tilt |
| Thinking | Upward gaze | Thoughtful look |
| Sad | Downward look | Somber expression |
| Surprised | Pull-back | Quick startled reaction |
| Neutral | Gentle idle | Calm breathing motion |
| Agreeing | Nod | Affirmative head nod |

## 💻 Usage Examples

### Interactive Mode

```bash
python main.py
```

```
RAT ASSISTANT - ANIMATED MODE
================================================================

You: Hello! What's your favorite season?

[Processing...]

Rat Assistant [happy]: Hello! I absolutely love autumn! The crisp air 
and the way the water feels just perfect for swimming makes it wonderful.

You: Can you explain quantum entanglement?

[Processing...]

Rat Assistant [thinking]: Quantum entanglement is a fascinating phenomenon...
```

### Console-Only Mode

```bash
python main.py --console-only
```

Perfect for testing or when you don't need the animation window.

### Programmatic Usage

```python
from llm import AgentOrchestrator, AgentConfig

# Create orchestrator
config = AgentConfig.from_env()
orchestrator = AgentOrchestrator(config)

# Process input
result = orchestrator.process_user_input("Hello!")
print(result['message'])
print(f"Emotion: {result['emotion']}")
```

### Run Examples

```bash
python -m llm.example_usage
```

Demonstrates individual agent capabilities.

## ⚙️ Configuration

Create a `.env` file or set environment variables:

```bash
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4o-mini          # or gpt-4, gpt-3.5-turbo, etc.
LLM_TEMPERATURE=0.7            # 0.0 to 2.0
```

Or configure programmatically:

```python
from llm import AgentConfig

config = AgentConfig(
    api_key="your-key",
    model="gpt-4",
    temperature=0.8
)
```

## 🎨 Animation System

The animation system supports:

- **3D Models**: Procedural mesh generation
- **Bone Rigging**: Skeletal animation support
- **Behavior Scripts**: Declarative animation sequences
- **Real-time Rendering**: Hardware-accelerated OpenGL
- **Easing Functions**: Smooth motion interpolation

### Creating Custom Animations

```python
from animation import BehaviorScript

script = BehaviorScript("custom")
script.rotate(x=30, duration=1.0, easing="ease_in_out")
script.rotate(y=45, duration=0.5, easing="ease_out")
script.translate(z=2, duration=1.0, easing="linear")
```

## 🔧 Development

### Adding New Emotions

1. Edit `llm/animation_subagent.py`:

```python
@staticmethod
def _create_custom_emotion_animation() -> BehaviorScript:
    script = BehaviorScript("custom_emotion")
    script.rotate(x=15, z=10, duration=0.5)
    return script

# Add to ANIMATION_BEHAVIORS dictionary
ANIMATION_BEHAVIORS["custom"] = {
    "script": lambda: AnimationSubagent._create_custom_emotion_animation(),
    "description": "Custom emotion"
}
```

2. Update system prompt in `llm/config.py` to include the new emotion

### Testing Components

```bash
# Test animation system
cd animation
python rat_demo_gl.py

# Test LLM agents
python -m llm.example_usage

# Test full system console-only
python main.py --console-only
```

## 📚 Documentation

- [LLM System Documentation](llm/README.md) - Detailed agent architecture guide
- [Animation Quick Start](animation/QUICK_START_RIGGING.md) - Animation system guide
- [Rigging Guide](animation/RIGGING_GUIDE.md) - Skeletal rigging documentation

## 🐛 Troubleshooting

**Import errors for openai:**
```bash
pip install --upgrade openai
```

**No animation window:**
- Ensure ModernGL is installed: `pip install moderngl moderngl-window`
- Try console-only mode first: `python main.py --console-only`
- Check graphics drivers are up to date

**API rate limits:**
- Use console-only mode for development
- Lower FPS in AnimationSystem initialization
- Reduce window size: `python main.py --width 640 --height 480`

## 🎯 Future Enhancements

- [ ] Speech-to-text input integration
- [ ] Text-to-speech output with voice synthesis
- [ ] Web interface (FastAPI + WebSocket)
- [ ] Multi-modal responses (text + actions)
- [ ] Conversation memory and personalization
- [ ] Support for other LLM providers (Anthropic, local models)
- [ ] Enhanced animation library
- [ ] Emotion intensity scaling
- [ ] Context-aware animation chaining

## 📝 License

Hackathon demonstration project.

## 🙏 Acknowledgments

- OpenAI for GPT models
- ModernGL for 3D rendering
- The rat community for inspiration
