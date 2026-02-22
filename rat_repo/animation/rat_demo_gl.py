"""
Rat Head Model Demo - ModernGL Version
Demonstrates the rat head model with hardware-accelerated Z-buffering.
"""

import numpy as np
from rat_model import RatModel
from animation_system import AnimationSystem
from behavior_script import BehaviorScript
from renderer_gl import GLAnimationPlayer


def demo_rat_turnaround_gl():
    """Demo: Rat head rotating with ModernGL renderer."""
    print("\nDemo: Rat Head Turnaround Loop (ModernGL)")
    print("=" * 50)
    print("Press ESC to stop the animation and close the window")
    print("=" * 50)
    
    # Create rat model
    rat = RatModel("river_rat")
    
    # Create animation system
    anim_system = AnimationSystem(rat, width=800, height=600, fps=30)
    
    # Apply 180-degree Z-axis rotation before streaming
    anim_system.set_state(rotation=np.array([0.0, 0.0, 180.0]))
    
    # Create behavior script - loop rotation around Y-axis indefinitely
    # Using a large number of iterations (effectively infinite)
    script = BehaviorScript()
    for i in range(100):  # 100 loops = ~17 minutes of animation
        script.rotate(0, 360, 0, duration=10.0, easing="linear")  # Slower rotation (10 seconds per revolution)
    
    # Play animation with GL renderer
    player = GLAnimationPlayer(anim_system, title="Rat Head - ModernGL (Press ESC to quit)", width=800, height=600)
    player.play(script, show_info=True)
    
    print("\nAnimation complete!")


def demo_rat_nod_gl():
    """Demo: Rat nodding with ModernGL renderer."""
    print("\nDemo: Rat Head Nodding (ModernGL)")
    print("=" * 50)
    
    # Create rat model
    rat = RatModel("nodding_rat")
    
    # Create animation system
    anim_system = AnimationSystem(rat, width=800, height=600, fps=30)
    
    # Create behavior script - nod up and down
    script = BehaviorScript()
    script.rotate(30, 0, 0, duration=1.0, easing="ease_in_out")
    script.rotate(-30, 0, 0, duration=1.0, easing="ease_in_out")
    script.rotate(30, 0, 0, duration=1.0, easing="ease_in_out")
    script.rotate(-30, 0, 0, duration=1.0, easing="ease_in_out")
    
    # Play with GL renderer (orientation fix applied automatically)
    player = GLAnimationPlayer(anim_system, title="Nodding Rat - ModernGL", width=800, height=600)
    player.play(script, show_info=True)
    
    print("\nAnimation complete!")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("RAT HEAD MODEL DEMOS - MODERNGL")
    print("=" * 50 + "\n")
    
    # Run turnaround demo
    demo_rat_turnaround_gl()
    
    # Uncomment to run other demos:
    # demo_rat_nod_gl()
