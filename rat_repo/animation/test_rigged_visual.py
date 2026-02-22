"""
Quick Rigged Model Visual Test
Run a single rigged animation demo to test visual output.
"""

from rigging import create_arm_skeleton
from model import RiggedModel
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
from renderer import quick_preview


def main():
    print("\n" + "="*60)
    print("RIGGED MODEL VISUAL TEST - Waving Arm")
    print("="*60)
    print("\nCreating a rigged arm that waves...")
    print("A window will open showing the animated rigged model.")
    print("Close the window when done viewing.\n")
    
    # Create arm skeleton
    skeleton = create_arm_skeleton()
    
    # Create rigged model
    model = RiggedModel("test_arm", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("shoulder", list(range(8)))
    
    # Waving animation targeting specific bones
    script = BehaviorScript("wave_test")
    
    # Wave at shoulder
    script.rotate(z=40, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-40, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=40, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-40, duration=0.5, easing='ease_in_out', bone="shoulder")
    
    # Bend at elbow
    script.rotate(y=90, duration=0.7, easing='ease_in_out', bone="elbow")
    script.rotate(y=-90, duration=0.7, easing='ease_in_out', bone="elbow")
    
    # Create animation system (800x600, 30fps)
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    # Show the animation in a window
    print("Opening window...")
    quick_preview(anim, script, title="Rigged Waving Arm - Test", realtime=True)
    
    print("\n" + "="*60)
    print("Test complete! Rigged model rendering is working.")
    print("="*60)
    print("\nRun 'python rigged_visual_demo.py' for more rigged demos!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
