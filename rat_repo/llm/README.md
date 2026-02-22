# LLM Agentic Architecture for Rat Assistant

An intelligent conversational agent system with an animated rat avatar. The system uses a multi-agent architecture where different AI agents handle conversation, message processing, and emotional animation.

## Architecture

### Core Components

1. **Driver Agent** (`driver_agent.py`)
   - Main conversational AI that processes user input
   - Maintains conversation history
   - Generates contextual responses

2. **Animation Subagent** (`animation_subagent.py`)
   - Analyzes emotional content of messages
   - Maps emotions to appropriate rat animations
   - Generates behavior scripts for the animation system

3. **Message Subagent** (`message_subagent.py`)
   - Refines and formats messages for display
   - Ensures clarity and friendliness
   - Handles console formatting

4. **Orchestrator** (`orchestrator.py`)
   - Coordinates all agents
   - Manages the conversation loop
   - Controls animation playback
   - Provides both console and animated modes


## Features

- **Emotional Animation**: The rat avatar expresses emotions (happy, sad, curious, excited, thinking, etc.)
- **Multi-Agent Design**: Specialized agents handle different aspects of the interaction
- **Console or Animated Mode**: Run with or without the animation window
- **Configurable**: Easy configuration via environment variables or code

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

Alternatively, create a `.env` file:

```
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
```

## Usage

### Run with Animation

```bash
python main.py
```

This starts the rat assistant with an animated window showing the rat avatar.

### Run Console-Only Mode

```bash
python main.py --console-only
```

This runs the assistant in text-only mode without opening the animation window.

### Custom Window Size

```bash
python main.py --width 1024 --height 768
```

## How It Works

### Conversation Flow

1. **User Input**: User types a message in the console
2. **Driver Agent**: Processes the input and generates a response
3. **Animation Subagent**: Analyzes the response to determine emotion
4. **Animation Generation**: Creates appropriate animation behavior script
5. **Display**: Shows the response text and plays animation simultaneously

### Emotion Mapping

The animation subagent maps detected emotions to animations:

- **Happy**: Upward head bob
- **Excited**: Enthusiastic wiggle
- **Curious**: Inquisitive head tilt
- **Thinking**: Thoughtful upward gaze
- **Sad**: Downward look
- **Surprised**: Quick pull-back
- **Concerned**: Worried tilt
- **Neutral**: Gentle idle breathing
- **Agreeing**: Affirmative nod
- **Disagreeing**: Head shake

## Configuration

Edit `llm/config.py` to customize:

- **Model**: Change the LLM model (default: gpt-4o-mini)
- **Temperature**: Adjust response creativity (default: 0.7)
- **System Prompts**: Customize agent personalities
- **Max Tokens**: Control response length

## Example Session

```
RAT ASSISTANT - ANIMATED MODE
================================================================
Starting animation window...
Type 'quit' or 'exit' to end the conversation
================================================================

You: Hello! How are you today?

[Processing...]

Rat Assistant [happy]: Hello there! I'm doing wonderfully, thank you for asking! 
How can I help you today?

You: Can you explain what quantum computing is?

[Processing...]

Rat Assistant [thinking]: Quantum computing is a fascinating field! It uses the 
principles of quantum mechanics to process information in ways that classical 
computers cannot...
```

## Future Enhancements

- Speech-to-text input integration
- Text-to-speech output
- More sophisticated emotion detection
- Multi-modal responses (text + suggestions)
- Conversation memory and personalization
- Additional animation behaviors
- Web interface

## Development

### Adding New Emotions

1. Add emotion to `AnimationSubagent.ANIMATION_BEHAVIORS`
2. Create static method for animation (e.g., `_create_emotion_animation()`)
3. Update system prompt in `config.py` to include new emotion

### Customizing Animations

Edit the animation creation methods in `animation_subagent.py`:

```python
@staticmethod
def _create_custom_animation() -> BehaviorScript:
    script = BehaviorScript("custom")
    script.rotate(x=10, y=5, z=0, duration=0.5, easing="ease_in_out")
    return script
```

## Troubleshooting

**No animation window appears**:
- Ensure ModernGL dependencies are installed
- Try console-only mode first to test LLM integration

**API Key errors**:
- Verify OPENAI_API_KEY is set correctly
- Check API key has credits available

**Import errors**:
- Ensure you're running from the project root directory
- Verify all dependencies are installed

## License

This project is part of a hackathon demonstration.
