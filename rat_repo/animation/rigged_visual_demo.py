"""
Visual Rigged Animation Demos
Shows rigged model animations in a window.
"""

from rigging import create_simple_skeleton, create_arm_skeleton, Skeleton
from model import RiggedModel
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
from renderer import AnimationPlayer, quick_preview
import numpy as np


def demo_waving_arm():
    """Demo: Arm waving animation."""
    print("\n" + "="*60)
    print("VISUAL DEMO 1: Waving Arm")
    print("="*60)
    print("Creating an arm that waves...")
    
    # Create arm
    skeleton = create_arm_skeleton()
    model = RiggedModel("waving_arm", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("shoulder", list(range(8)))
    
    # Wave animation
    script = BehaviorScript("wave")
    script.rotate(z=30, duration=0.4, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-30, duration=0.4, easing='ease_in_out', bone="shoulder")
    script.rotate(z=30, duration=0.4, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-30, duration=0.4, easing='ease_in_out', bone="shoulder")
    script.rotate(z=30, duration=0.4, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-30, duration=0.4, easing='ease_in_out', bone="shoulder")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Waving Arm", realtime=True)
    print("Demo 1 complete!\n")


def demo_bending_arm():
    """Demo: Arm bending at elbow."""
    print("\n" + "="*60)
    print("VISUAL DEMO 2: Bending Arm")
    print("="*60)
    print("Creating an arm that bends at the elbow...")
    
    skeleton = create_arm_skeleton()
    model = RiggedModel("bending_arm", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("shoulder", list(range(8)))
    
    # Bend animation
    script = BehaviorScript("bend")
    script.rotate(y=90, duration=1.0, easing='ease_in_out', bone="elbow")
    script.rotate(y=-90, duration=1.0, easing='ease_in_out', bone="elbow")
    script.rotate(y=90, duration=1.0, easing='ease_in_out', bone="elbow")
    script.rotate(y=-90, duration=1.0, easing='ease_in_out', bone="elbow")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Bending Arm", realtime=True)
    print("Demo 2 complete!\n")


def demo_coordinated_movement():
    """Demo: Multiple bones moving together."""
    print("\n" + "="*60)
    print("VISUAL DEMO 3: Coordinated Movement")
    print("="*60)
    print("Creating coordinated multi-bone animation...")
    
    skeleton = create_arm_skeleton()
    model = RiggedModel("coordinated_arm", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("shoulder", list(range(8)))
    
    # Complex choreography
    script = BehaviorScript("coordinated")
    
    # Lift shoulder
    script.rotate(z=45, duration=0.5, easing='ease_out', bone="shoulder")
    
    # Bend elbow
    script.rotate(y=90, duration=0.5, easing='ease_in_out', bone="elbow")
    
    # Rotate wrist
    script.rotate(x=360, duration=1.5, easing='linear', bone="wrist")
    
    # Unbend elbow
    script.rotate(y=-90, duration=0.5, easing='ease_in_out', bone="elbow")
    
    # Lower shoulder
    script.rotate(z=-45, duration=0.5, easing='ease_in', bone="shoulder")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Coordinated Movement", realtime=True)
    print("Demo 3 complete!\n")


def demo_walking_motion():
    """Demo: Simple walking leg motion."""
    print("\n" + "="*60)
    print("VISUAL DEMO 4: Walking Motion")
    print("="*60)
    print("Creating a walking animation...")
    
    skeleton = create_simple_skeleton()
    model = RiggedModel("walker", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("torso", list(range(8)))
    
    # Walking script
    script = BehaviorScript("walk_cycle")
    
    # Step 1: Left leg forward, right back
    script.rotate(x=30, duration=0.3, easing='ease_in_out', bone="left_hip")
    script.rotate(x=-30, duration=0.3, easing='ease_in_out', bone="right_hip")
    
    # Step 2: Reverse
    script.rotate(x=-60, duration=0.6, easing='ease_in_out', bone="left_hip")
    script.rotate(x=60, duration=0.6, easing='ease_in_out', bone="right_hip")
    
    # Step 3: Back to forward
    script.rotate(x=60, duration=0.6, easing='ease_in_out', bone="left_hip")
    script.rotate(x=-60, duration=0.6, easing='ease_in_out', bone="right_hip")
    
    # Step 4: Return to center
    script.rotate(x=-30, duration=0.3, easing='ease_in_out', bone="left_hip")
    script.rotate(x=30, duration=0.3, easing='ease_in_out', bone="right_hip")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    player = AnimationPlayer(anim, title="Walking Motion", realtime=True)
    player.play_loop(script, iterations=2)
    print("Demo 4 complete!\n")


def demo_snake_tail():
    """Demo: Undulating snake tail."""
    print("\n" + "="*60)
    print("VISUAL DEMO 5: Snake Tail")
    print("="*60)
    print("Creating an undulating tail with multiple segments...")
    
    # Create snake tail skeleton
    skeleton = Skeleton("snake")
    skeleton.add_bone("base")
    for i in range(1, 6):
        skeleton.add_bone(f"segment{i}", parent_name=f"segment{i-1}" if i > 1 else "base",
                         position=np.array([0.0, 0.0, 1.0]))
    
    model = RiggedModel("snake_tail", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("base", list(range(8)))
    
    # Undulating wave motion
    script = BehaviorScript("undulate")
    
    # Wave going down the tail
    for i in range(1, 6):
        script.rotate(x=25, duration=0.15, easing='ease_in_out', bone=f"segment{i}")
    
    # Reverse wave
    for i in range(1, 6):
        script.rotate(x=-50, duration=0.3, easing='ease_in_out', bone=f"segment{i}")
    
    # Back to center
    for i in range(1, 6):
        script.rotate(x=25, duration=0.15, easing='ease_in_out', bone=f"segment{i}")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("Opening window... (Close window to continue)")
    player = AnimationPlayer(anim, title="Snake Tail", realtime=True)
    player.play_loop(script, iterations=3)
    print("Demo 5 complete!\n")


def demo_full_body_gesture():
    """Demo: Full body with multiple parts moving."""
    print("\n" + "="*60)
    print("VISUAL DEMO 6: Full Body Gesture")
    print("="*60)
    print("Creating complex full-body animation...")
    
    skeleton = create_simple_skeleton()
    model = RiggedModel("full_body", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("torso", list(range(8)))
    
    # Complex gesture
    script = BehaviorScript("gesture")
    
    # Raise arms
    script.rotate(z=80, duration=0.6, easing='ease_out', bone="left_shoulder")
    script.rotate(z=-80, duration=0.6, easing='ease_out', bone="right_shoulder")
    
    # Nod head
    script.rotate(x=15, duration=0.3, easing='ease_in_out', bone="head")
    script.rotate(x=-30, duration=0.3, easing='ease_in_out', bone="head")
    script.rotate(x=15, duration=0.3, easing='ease_in_out', bone="head")
    
    # Bend arms
    script.rotate(y=80, duration=0.4, easing='ease_in_out', bone="left_elbow")
    script.rotate(y=-80, duration=0.4, easing='ease_in_out', bone="right_elbow")
    
    # Wave hands
    script.rotate(z=30, duration=0.2, easing='ease_in_out', bone="left_hand")
    script.rotate(z=-30, duration=0.2, easing='ease_in_out', bone="left_hand")
    script.rotate(z=30, duration=0.2, easing='ease_in_out', bone="left_hand")
    script.rotate(z=-30, duration=0.2, easing='ease_in_out', bone="left_hand")
    
    script.rotate(z=-30, duration=0.2, easing='ease_in_out', bone="right_hand")
    script.rotate(z=30, duration=0.2, easing='ease_in_out', bone="right_hand")
    script.rotate(z=-30, duration=0.2, easing='ease_in_out', bone="right_hand")
    script.rotate(z=30, duration=0.2, easing='ease_in_out', bone="right_hand")
    
    # Lower arms
    script.rotate(y=-80, duration=0.4, easing='ease_in_out', bone="left_elbow")
    script.rotate(y=80, duration=0.4, easing='ease_in_out', bone="right_elbow")
    script.rotate(z=-80, duration=0.6, easing='ease_in', bone="left_shoulder")
    script.rotate(z=80, duration=0.6, easing='ease_in', bone="right_shoulder")
    
    anim = AnimationSystem(model, width=1024, height=768, fps=30)
    
    print("Opening window... (Close window to continue)")
    quick_preview(anim, script, title="Full Body Gesture", realtime=True)
    print("Demo 6 complete!\n")


def main():
    """Run all visual rigged model demos."""
    print("\n" + "="*60)
    print("VISUAL RIGGED MODEL ANIMATION DEMOS")
    print("="*60)
    print("\nThese demos show rigged models with bone animations.")
    print("Close each window to proceed to the next demo.")
    print("\nPress Ctrl+C at any time to exit.")
    
    try:
        demo_waving_arm()
        demo_bending_arm()
        demo_coordinated_movement()
        demo_walking_motion()
        demo_snake_tail()
        demo_full_body_gesture()
        
        print("\n" + "="*60)
        print("ALL RIGGED MODEL DEMOS COMPLETE!")
        print("="*60)
        print("\nYou've seen:")
        print("  ✓ Individual bone targeting")
        print("  ✓ Hierarchical transformations")
        print("  ✓ Multi-bone coordination")
        print("  ✓ Complex choreography")
        print("  ✓ Looping animations")
        print("\nYour animation system now supports full rigging!")
        print("="*60 + "\n")
    
    except KeyboardInterrupt:
        print("\n\nDemos interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError during demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
