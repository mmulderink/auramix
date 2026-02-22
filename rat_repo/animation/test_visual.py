"""
Quick Visual Test
Run a single animation demo to test the visual output.
"""

from model import Model3D
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
from renderer import quick_preview


def main():
    print("\n" + "="*60)
    print("VISUAL OUTPUT TEST - Spinning Cube")
    print("="*60)
    print("\nCreating a simple spinning cube animation...")
    print("A window will open showing the animated 3D cube.")
    print("Close the window when done viewing.\n")
    
    # Create model
    model = Model3D(name="test_cube")
    
    # Create animation script - rotating cube
    script = BehaviorScript("spin_test")
    script.rotate(y=720, duration=4.0, easing='linear')  # Two full rotations
    
    # Create animation system (800x600, 30fps)
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    # Show the animation in a window
    print("Opening window...")
    quick_preview(anim, script, title="Spinning Cube - Test", realtime=True)
    
    print("\n" + "="*60)
    print("Test complete! The visual renderer is working.")
    print("="*60)
    print("\nRun 'python visual_demo.py' for more animation demos!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
