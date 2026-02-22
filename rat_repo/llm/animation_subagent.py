"""
Animation Controller Subagent
Analyzes message content and controls the rat avatar animations.
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from animation.behavior_script import BehaviorScript
from .config import AgentConfig


def _extract_response_text(response) -> str:
    if getattr(response, "output_text", None):
        return response.output_text

    try:
        for item in response.output:
            for content in item.content:
                if getattr(content, "type", None) == "output_text" and getattr(content, "text", None):
                    return content.text
    except Exception:
        pass

    return ""


class AnimationSubagent:
    """
    Subagent responsible for controlling animations based on message content.
    Analyzes emotional tone and intent to trigger appropriate rat animations.
    """
    
    # Animation behavior definitions
    ANIMATION_BEHAVIORS = {
        "happy": {
            "script": lambda: AnimationSubagent._create_happy_animation(),
            "description": "Joyful head bob"
        },
        "excited": {
            "script": lambda: AnimationSubagent._create_excited_animation(),
            "description": "Enthusiastic wiggle"
        },
        "curious": {
            "script": lambda: AnimationSubagent._create_curious_animation(),
            "description": "Inquisitive tilt"
        },
        "thinking": {
            "script": lambda: AnimationSubagent._create_thinking_animation(),
            "description": "Thoughtful look"
        },
        "sad": {
            "script": lambda: AnimationSubagent._create_sad_animation(),
            "description": "Downward look"
        },
        "surprised": {
            "script": lambda: AnimationSubagent._create_surprised_animation(),
            "description": "Quick head pull-back"
        },
        "concerned": {
            "script": lambda: AnimationSubagent._create_concerned_animation(),
            "description": "Worried tilt"
        },
        "neutral": {
            "script": lambda: AnimationSubagent._create_neutral_animation(),
            "description": "Gentle idle movement"
        },
        "agreeing": {
            "script": lambda: AnimationSubagent._create_nod_animation(),
            "description": "Affirmative nod"
        },
        "disagreeing": {
            "script": lambda: AnimationSubagent._create_shake_animation(),
            "description": "Head shake"
        }
    }
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the animation subagent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.system_prompt = config.animation_system_prompt
    
    def analyze_and_animate(self, message: str) -> tuple[BehaviorScript, Dict[str, Any]]:
        """
        Analyze message and return appropriate animation.
        
        Args:
            message: The message to analyze
            
        Returns:
            Tuple of (BehaviorScript, analysis_data)
        """
        analysis = self._analyze_emotion(message)
        script = self._create_animation_from_analysis(analysis)
        return script, analysis
    
    def _analyze_emotion(self, message: str) -> Dict[str, Any]:
        """
        Use LLM to analyze emotional content of message.
        
        Args:
            message: Message to analyze
            
        Returns:
            Dictionary with emotion, intensity, and suggested animation
        """
        prompt = f"""Analyze this message and determine the appropriate emotion and animation:

Message: "{message}"

Respond with ONLY a JSON object, no other text."""
        
        try:
            response = self.client.responses.create(
                model=self.config.model,
                input=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = _extract_response_text(response).strip()
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return pure JSON
                print(f"Warning: Could not parse JSON response: {response_text}")
                analysis = {"emotion": "neutral", "intensity": "medium", "animation": "neutral_idle"}
            
            return analysis
            
        except Exception as e:
            print(f"Animation Analysis Error: {str(e)}")
            # Default to neutral
            return {"emotion": "neutral", "intensity": "medium", "animation": "neutral_idle"}
    
    def _create_animation_from_analysis(self, analysis: Dict[str, Any]) -> BehaviorScript:
        """
        Create a behavior script based on emotion analysis.
        
        Args:
            analysis: Emotion analysis data
            
        Returns:
            BehaviorScript for the animation
        """
        emotion = analysis.get("emotion", "neutral").lower()
        intensity = analysis.get("intensity", "medium").lower()
        
        # Map emotion to behavior
        animation_key = emotion
        if animation_key not in self.ANIMATION_BEHAVIORS:
            animation_key = "neutral"
        
        # Get base animation script
        script = self.ANIMATION_BEHAVIORS[animation_key]["script"]()
        
        # Modify based on intensity (future enhancement)
        # For now, just return the base script
        
        return script
    
    # Animation creation methods
    @staticmethod
    def _create_happy_animation() -> BehaviorScript:
        """Create happy/joyful animation - upward bob."""
        script = BehaviorScript("happy")
        script.set_effect("stars", duration=1.6)
        script.translate(y=1.4, duration=0.45, easing="ease_out_cubic")
        script.translate(y=-0.5, duration=0.25, easing="ease_in_cubic")
        script.translate(y=0.2, duration=0.2, easing="ease_out")
        script.rotate(x=25, z=18, duration=0.45, easing="ease_out_cubic")
        script.rotate(x=-12, z=-8, duration=0.3, easing="ease_in_out")
        script.rotate(x=0, z=0, duration=0.4, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=1.1)
        return script
    
    @staticmethod
    def _create_excited_animation() -> BehaviorScript:
        """Create excited animation - enthusiastic wiggle."""
        script = BehaviorScript("excited")
        script.set_effect("stars", duration=1.8)
        for _ in range(3):
            script.rotate(z=28, y=12, duration=0.25, easing="ease_in_out")
            script.rotate(z=-28, y=-12, duration=0.25, easing="ease_in_out")
        script.translate(y=1.0, duration=0.35, easing="ease_out_cubic")
        script.translate(y=-0.6, duration=0.25, easing="ease_in_cubic")
        script.translate(y=0.2, duration=0.2, easing="ease_out")
        script.rotate(z=0, y=0, duration=0.35, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=1.4)
        return script
    
    @staticmethod
    def _create_curious_animation() -> BehaviorScript:
        """Create curious animation - tilt head."""
        script = BehaviorScript("curious")
        script.rotate(z=32, y=12, duration=0.55, easing="ease_out_cubic")
        script.rotate(z=-18, y=-12, duration=0.45, easing="ease_in_out")
        script.rotate(z=6, y=4, duration=0.3, easing="ease_out")
        script.rotate(z=0, y=0, duration=0.35, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.9)
        return script
    
    @staticmethod
    def _create_thinking_animation() -> BehaviorScript:
        """Create thinking animation - slight upward tilt."""
        script = BehaviorScript("thinking")
        script.rotate(x=22, z=16, duration=0.7, easing="ease_out_cubic")
        script.rotate(x=8, z=-10, duration=0.5, easing="ease_in_out")
        script.rotate(x=2, z=6, duration=0.35, easing="ease_out")
        script.rotate(x=0, z=0, duration=0.4, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.6)
        return script
    
    @staticmethod
    def _create_sad_animation() -> BehaviorScript:
        """Create sad animation - downward look."""
        script = BehaviorScript("sad")
        script.set_effect("tears", duration=2.0)
        script.translate(y=-1.0, duration=0.8, easing="ease_out_cubic")
        script.rotate(x=-28, duration=0.9, easing="ease_out_cubic")
        script.rotate(x=-10, duration=0.5, easing="ease_in_out")
        script.translate(y=0.4, duration=0.45, easing="ease_out")
        script.translate(y=-0.2, duration=0.35, easing="ease_in")
        script.rotate(x=0, duration=0.6, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.4)
        return script
    
    @staticmethod
    def _create_surprised_animation() -> BehaviorScript:
        """Create surprised animation - quick pull back."""
        script = BehaviorScript("surprised")
        script.set_effect("stars", duration=1.2)
        script.translate(z=1.4, duration=0.25, easing="ease_out_cubic")
        script.rotate(x=32, duration=0.25, easing="ease_out_cubic")
        script.translate(z=-1.1, duration=0.35, easing="ease_in_out")
        script.rotate(x=-10, duration=0.35, easing="ease_in_out")
        script.rotate(x=0, duration=0.35, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=1.0)
        return script
    
    @staticmethod
    def _create_concerned_animation() -> BehaviorScript:
        """Create concerned animation - worried tilt."""
        script = BehaviorScript("concerned")
        script.rotate(z=-28, x=-12, duration=0.7, easing="ease_out_cubic")
        script.rotate(z=12, x=6, duration=0.55, easing="ease_in_out")
        script.rotate(z=-6, x=-3, duration=0.35, easing="ease_out")
        script.rotate(z=0, x=0, duration=0.45, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.7)
        return script
    
    @staticmethod
    def _create_neutral_animation() -> BehaviorScript:
        """Create neutral/idle animation - gentle breathing motion."""
        script = BehaviorScript("neutral")
        script.rotate(x=6, duration=1.4, easing="ease_in_out")
        script.rotate(x=-6, duration=1.4, easing="ease_in_out")
        script.rotate(x=0, duration=0.8, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.3)
        return script
    
    @staticmethod
    def _create_nod_animation() -> BehaviorScript:
        """Create nodding animation - yes."""
        script = BehaviorScript("nod")
        for _ in range(2):
            script.rotate(x=28, duration=0.35, easing="ease_in_out")
            script.rotate(x=-18, duration=0.3, easing="ease_in_out")
        script.rotate(x=6, duration=0.25, easing="ease_out")
        script.rotate(x=0, duration=0.35, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.8)
        return script
    
    @staticmethod
    def _create_shake_animation() -> BehaviorScript:
        """Create head shake animation - no."""
        script = BehaviorScript("shake")
        for _ in range(2):
            script.rotate(y=32, duration=0.3, easing="ease_in_out")
            script.rotate(y=-32, duration=0.3, easing="ease_in_out")
        script.rotate(y=8, duration=0.25, easing="ease_out")
        script.rotate(y=0, duration=0.35, easing="ease_in_out")
        AnimationSubagent._add_nose_wiggle(script, intensity=0.9)
        return script

    @staticmethod
    def _add_nose_wiggle(script: BehaviorScript, intensity: float = 1.0):
        amp = 10.0 * max(0.1, intensity)
        script.rotate(y=amp, duration=0.12, easing="ease_in_out", bone="nose")
        script.rotate(y=-amp, duration=0.12, easing="ease_in_out", bone="nose")
        script.rotate(y=amp * 0.5, duration=0.1, easing="ease_in_out", bone="nose")
        script.rotate(y=0, duration=0.1, easing="ease_in_out", bone="nose")
