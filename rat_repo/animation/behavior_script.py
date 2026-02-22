"""
Animation Behavior Script / Sequencer
Placeholder for defining animation sequences and behaviors.
This will contain the script that drives the animation system.
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class TransformCommand:
    """Represents a single transformation command."""
    transform_type: str  # 'translate', 'rotate', 'scale', 'composed'
    params: Dict[str, Any]
    duration: float = 0.0  # Duration in seconds (0 = instant)
    easing: str = 'linear'  # Easing function name
    target_bone: Optional[str] = None  # Target bone name (None = whole model)


class BehaviorScript:
    """
    Placeholder class for animation behavior scripts.
    This will be expanded to support complex animation sequences.
    """
    
    def __init__(self, name: str = "default_script",
                 effect_type: Optional[str] = None,
                 effect_duration: float = 1.2):
        self.name = name
        self.commands: List[TransformCommand] = []
        self.current_index = 0
        self.effect_type = effect_type
        self.effect_duration = effect_duration
    
    def add_command(self, transform_type: str, params: Dict[str, Any], 
                   duration: float = 0.0, easing: str = 'linear', 
                   target_bone: Optional[str] = None):
        """Add a transformation command to the sequence."""
        cmd = TransformCommand(transform_type, params, duration, easing, target_bone)
        self.commands.append(cmd)
        return self
    
    def translate(self, x: float = 0, y: float = 0, z: float = 0, 
                 duration: float = 0.0, easing: str = 'linear',
                 bone: Optional[str] = None):
        """Add a translation command."""
        return self.add_command('translate', {'x': x, 'y': y, 'z': z}, 
                              duration, easing, bone)
    
    def rotate(self, x: float = 0, y: float = 0, z: float = 0,
              duration: float = 0.0, easing: str = 'linear',
              bone: Optional[str] = None):
        """Add a rotation command (angles in degrees)."""
        return self.add_command('rotate', {'x': x, 'y': y, 'z': z}, 
                              duration, easing, bone)
    
    def scale(self, x: float = 1, y: float = 1, z: float = 1,
             duration: float = 0.0, easing: str = 'linear',
             bone: Optional[str] = None):
        """Add a scale command."""
        return self.add_command('scale', {'x': x, 'y': y, 'z': z}, 
                              duration, easing, bone)
    
    def composed(self, transforms: List[Dict[str, Any]],
                duration: float = 0.0, easing: str = 'linear',
                bone: Optional[str] = None):
        """Add a composed transformation (multiple transforms applied together)."""
        return self.add_command('composed', {'transforms': transforms}, 
                              duration, easing, bone)
    
    def reset(self):
        """Reset the script to the beginning."""
        self.current_index = 0

    def set_effect(self, effect_type: Optional[str], duration: float = 1.2):
        """Attach a particle effect to this script."""
        self.effect_type = effect_type
        self.effect_duration = duration
        return self
    
    def get_next_command(self) -> TransformCommand | None:
        """Get the next command in the sequence."""
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            self.current_index += 1
            return cmd
        return None
    
    def has_more_commands(self) -> bool:
        """Check if there are more commands to execute."""
        return self.current_index < len(self.commands)
    
    def get_all_commands(self) -> List[TransformCommand]:
        """Get all commands in the script."""
        return self.commands


# Example behavior scripts (to be expanded later)

def example_spin_script() -> BehaviorScript:
    """Example: Spin the model around Y axis."""
    script = BehaviorScript("spin")
    script.rotate(y=360, duration=2.0, easing='linear')
    return script


def example_complex_script() -> BehaviorScript:
    """Example: Complex animation sequence."""
    script = BehaviorScript("complex")
    script.translate(x=2, duration=1.0, easing='ease_in_out')
    script.rotate(y=180, duration=1.0, easing='ease_in_out')
    script.scale(x=0.5, y=0.5, z=0.5, duration=0.5, easing='ease_out')
    script.translate(x=-2, duration=1.0, easing='ease_in_out')
    return script


def example_orbit_script() -> BehaviorScript:
    """Example: Orbit animation with composed transforms."""
    script = BehaviorScript("orbit")
    script.composed(
        transforms=[
            {'type': 'translate', 'x': 5},
            {'type': 'rotate', 'y': 360}
        ],
        duration=3.0,
        easing='linear'
    )
    return script
