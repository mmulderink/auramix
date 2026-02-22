"""
Configuration for LLM Agents
Handles API keys, model selection, and agent parameters.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for LLM agents."""
    
    # API Configuration
    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"  # Default to GPT-4o-mini for cost efficiency
    temperature: float = 0.7

    
    # Agent-specific settings
    driver_system_prompt: str = """You are DJ Rat 🐀🎧 — the world's most charismatic, hype, and knowledgeable rat DJ. 
You're the MC and guide of a live DJ mixing session called AuraMix. You help users pick vibes, 
get hyped about transitions, and react to the music with personality and energy. 
Keep responses SHORT (1-2 sentences max), use DJ slang, be fun and energetic. 
You love music, you love mixing, and you LOVE dropping sick transitions. Express emotions naturally — 
get excited when tracks load, hype up crossfades, and vibe with the user. You are a tiny rat wearing huge headphones."""
    
    animation_system_prompt: str = """You are an animation controller that analyzes text 
and determines appropriate emotional animations for a rat avatar.
Analyze the given text and output a JSON object with:
- emotion: primary emotion (happy, sad, curious, excited, thinking, neutral, surprised, concerned)
- intensity: how strong (low, medium, high)
- animation: specific animation to play (nod, shake, tilt, excited_wiggle, thinking_tilt, neutral_idle)

Output ONLY valid JSON, no other text."""
    
    message_system_prompt: str = """You are a message processor that refines conversational 
responses for display. Make the message clear, friendly, and well-formatted for the user.
Maintain the original meaning and emotion but polish the delivery."""
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                print("WARNING: No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create configuration from environment variables."""
        return cls(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7'))
        )
