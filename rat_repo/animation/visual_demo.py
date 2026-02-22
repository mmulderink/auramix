"""
Visual Animation Examples
Demonstrates animations with real-time window rendering.
"""

from model import Model3D
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
from renderer import AnimationPlayer, quick_preview


def demo_spinning_cube():
    """Demo: Simple spinning cube."""
    print("\n" + "="*60)
    print("DEMO 1: Spinning Cube")
    print("="*60)
    print("Creating a spinning cube animation...")
    
    # Create model and script
    model = Model3D(name="spinning_cube")
    script = BehaviorScript("spin")
    script.rotate(y=360, duration=3.0, easing='linear')
    
    # Create animation system
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    # Play animation
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Spinning Cube", realtime=True)
    print("Demo 1 complete!\n")


def demo_complex_movement():
    """Demo: Complex movement sequence."""
    print("\n" + "="*60)
    print("DEMO 2: Complex Movement")
    print("="*60)
    print("Creating a complex animation sequence...")
    
    model = Model3D(name="dancing_cube")
    
    # Create complex choreography
    script = BehaviorScript("dance")
    script.translate(x=3, duration=1.0, easing='ease_in_out')
    script.rotate(y=180, z=45, duration=1.0, easing='ease_in_out')
    script.translate(y=2, duration=0.8, easing='ease_out')
    script.scale(x=0.5, y=0.5, z=0.5, duration=0.5, easing='ease_in')
    script.rotate(x=360, y=180, duration=1.5, easing='linear')
    script.translate(x=-3, y=-2, duration=1.2, easing='ease_in_out')
    script.scale(x=2, y=2, z=2, duration=0.7, easing='ease_out')
    script.rotate(z=-45, duration=0.5, easing='ease_in_out')
    
    anim = AnimationSystem(model, width=1024, height=768, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Complex Movement", realtime=True)
    print("Demo 2 complete!\n")


def demo_orbit():
    """Demo: Orbital motion using composed transforms."""
    print("\n" + "="*60)
    print("DEMO 3: Orbital Animation")
    print("="*60)
    print("Creating orbital motion with composed transforms...")
    
    model = Model3D(name="orbiting_cube")
    
    script = BehaviorScript("orbit")
    # Orbit around center while rotating
    script.composed(
        transforms=[
            {'type': 'translate', 'x': 4},
            {'type': 'rotate', 'y': 360}
        ],
        duration=4.0,
        easing='linear'
    )
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Orbital Motion", realtime=True)
    print("Demo 3 complete!\n")


def demo_pulsing():
    """Demo: Pulsing scale animation."""
    print("\n" + "="*60)
    print("DEMO 4: Pulsing Animation")
    print("="*60)
    print("Creating a pulsing effect...")
    
    model = Model3D(name="pulsing_cube")
    
    script = BehaviorScript("pulse")
    # Pulse in and out
    script.scale(x=1.5, y=1.5, z=1.5, duration=0.8, easing='ease_out')
    script.scale(x=1.0, y=1.0, z=1.0, duration=0.8, easing='ease_in')
    script.scale(x=1.5, y=1.5, z=1.5, duration=0.8, easing='ease_out')
    script.scale(x=1.0, y=1.0, z=1.0, duration=0.8, easing='ease_in')
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Pulsing Effect", realtime=True)
    print("Demo 4 complete!\n")


def demo_looping_animation():
    """Demo: Looping animation."""
    print("\n" + "="*60)
    print("DEMO 5: Looping Animation")
    print("="*60)
    print("Creating a looping animation (3 iterations)...")
    
    model = Model3D(name="looping_cube")
    
    script = BehaviorScript("loop_sequence")
    script.rotate(y=120, duration=1.0, easing='ease_in_out')
    script.translate(x=2, duration=0.5, easing='ease_out')
    script.rotate(y=120, duration=1.0, easing='ease_in_out')
    script.translate(x=-2, duration=0.5, easing='ease_in')
    script.rotate(y=120, duration=1.0, easing='ease_in_out')
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    player = AnimationPlayer(anim, title="Looping Animation", realtime=True)
    player.play_loop(script, iterations=3)
    print("Demo 5 complete!\n")


def demo_showcase():
    """Demo: Ultimate showcase with multiple effects."""
    print("\n" + "="*60)
    print("DEMO 6: Ultimate Showcase")
    print("="*60)
    print("Creating the ultimate animation showcase...")
    
    model = Model3D(name="showcase_cube")
    
    script = BehaviorScript("showcase")
    
    # Enter from left with spin
    script.translate(x=-5, duration=0.0)  # Start off-screen
    script.composed(
        transforms=[
            {'type': 'translate', 'x': 5},
            {'type': 'rotate', 'z': 360}
        ],
        duration=2.0,
        easing='ease_out'
    )
    
    # Center spin and grow
    script.composed(
        transforms=[
            {'type': 'rotate', 'y': 360, 'x': 180},
            {'type': 'scale', 'x': 1.5, 'y': 1.5, 'z': 1.5}
        ],
        duration=2.0,
        easing='ease_in_out'
    )
    
    # Dance around
    script.translate(x=2, y=2, duration=0.8, easing='ease_in_out')
    script.rotate(z=90, duration=0.5, easing='ease_in_out')
    script.translate(x=-4, duration=0.8, easing='ease_in_out')
    script.rotate(z=90, duration=0.5, easing='ease_in_out')
    script.translate(y=-4, duration=0.8, easing='ease_in_out')
    script.rotate(z=90, duration=0.5, easing='ease_in_out')
    script.translate(x=4, duration=0.8, easing='ease_in_out')
    script.rotate(z=90, duration=0.5, easing='ease_in_out')
    script.translate(y=2, duration=0.8, easing='ease_in_out')
    
    # Final flourish and shrink away
    script.rotate(x=360, y=360, z=360, duration=2.0, easing='linear')
    script.composed(
        transforms=[
            {'type': 'scale', 'x': 0.1, 'y': 0.1, 'z': 0.1},
            {'type': 'rotate', 'y': 720}
        ],
        duration=2.0,
        easing='ease_in'
    )
    
    anim = AnimationSystem(model, width=1024, height=768, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Ultimate Showcase", realtime=True)
    print("Demo 6 complete!\n")


def main():
    """Run visual demos."""
    print("\n" + "="*60)
    print("VISUAL ANIMATION DEMOS")
    print("="*60)
    print("\nThese demos will open windows showing real-time animations.")
    print("Close each window to proceed to the next demo.")
    print("\nPress Ctrl+C at any time to exit.")
    
    try:
        demo_spinning_cube()
        demo_complex_movement()
        demo_orbit()
        demo_pulsing()
        demo_looping_animation()
        demo_showcase()
        
        print("\n" + "="*60)
        print("ALL VISUAL DEMOS COMPLETE!")
        print("="*60)
        print("\nThe animation system is ready for your custom animations!")
        print("Check README.md for usage documentation.\n")
    
    except KeyboardInterrupt:
        print("\n\nDemos interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError during demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
