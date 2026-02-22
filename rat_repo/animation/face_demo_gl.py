"""
Face Model Demo - ModernGL Version
Demonstrates the face model with hardware-accelerated Z-buffering.
"""

import numpy as np
from face_model import FaceModel
from animation_system import AnimationSystem
from behavior_script import BehaviorScript
from renderer_gl import GLAnimationPlayer


def demo_face_turnaround_gl():
    """Demo: Face rotating to show all angles with ModernGL."""
    print("\nDemo: Face Turnaround (ModernGL)")
    print("=" * 50)
    
    # Create face model
    face = FaceModel("bearded_face")
    
    # Create animation system
    anim_system = AnimationSystem(face, width=800, height=600, fps=30)
    
    # Create behavior script - rotate around Y-axis
    script = BehaviorScript()
    script.rotate(0, 360, 0, duration=8.0, easing="linear")
    
    # Play animation with GL renderer (orientation fix applied automatically)
    player = GLAnimationPlayer(anim_system, title="Bearded Face - ModernGL", width=800, height=600)
    player.play(script, show_info=True)
    
    print("\nAnimation complete!")


def demo_rotating_face_gl():
    """Demo: Face spinning continuously with ModernGL."""
    print("\nDemo: Rotating Face (ModernGL)")
    print("=" * 50)
    
    # Create face model
    face = FaceModel("spinning_face")
    
    # Create animation system
    anim_system = AnimationSystem(face, width=800, height=600, fps=30)
    
    # Multi-axis rotation
    script = BehaviorScript()
    script.rotate(360, 360, 0, duration=10.0, easing="linear")
    
    # Play with GL renderer (orientation fix applied automatically)
    player = GLAnimationPlayer(anim_system, title="Spinning Face - ModernGL", width=800, height=600)
    player.play(script, show_info=True)
    
    print("\nAnimation complete!")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("FACE MODEL DEMOS - MODERNGL")
    print("=" * 50 + "\n")
    
    # Run turnaround demo
    demo_face_turnaround_gl()
    
    # Uncomment to run other demos:
    # demo_rotating_face_gl()
