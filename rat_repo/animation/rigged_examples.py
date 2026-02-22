"""
Rigged Model Animation Examples
Demonstrates animations with skeletal rigging and bone targeting.
"""

from rigging import create_simple_skeleton, create_arm_skeleton, Skeleton
from model import RiggedModel, create_simple_rigged_cube, create_articulated_model
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
import numpy as np


def example_simple_arm():
    """Example: Animate an arm with multiple joints."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Animated Arm")
    print("="*60)
    print("Creating a rigged arm model with shoulder, elbow, wrist, hand...")
    
    # Create arm skeleton
    skeleton = create_arm_skeleton()
    print(f"\nSkeleton hierarchy:")
    print(skeleton.get_hierarchy_string())
    
    # Create rigged model
    model = RiggedModel("animated_arm", skeleton)
    model.set_cube_mesh()
    
    # Assign all vertices to shoulder bone for simplicity
    all_verts = list(range(8))
    model.attach_vertices_to_bone("shoulder", all_verts)
    
    # Create animation script - wave the arm
    script = BehaviorScript("wave_arm")
    
    # Rotate shoulder
    script.rotate(z=45, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-45, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=45, duration=0.5, easing='ease_in_out', bone="shoulder")
    script.rotate(z=-45, duration=0.5, easing='ease_in_out', bone="shoulder")
    
    # Bend elbow
    script.rotate(y=90, duration=0.5, easing='ease_in_out', bone="elbow")
    script.rotate(y=-90, duration=0.5, easing='ease_in_out', bone="elbow")
    
    # Rotate wrist
    script.rotate(x=180, duration=1.0, easing='linear', bone="wrist")
    
    # Create animation system
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    # Stream frames
    print("\nAnimating arm...")
    frame_count = 0
    for frame in anim.stream_frames(script):
        frame_count += 1
        if frame_count % 15 == 0:
            print(f"  Frame {frame.frame_number}: time={frame.timestamp:.2f}s")
    
    print(f"Generated {frame_count} frames\n")


def example_walking_legs():
    """Example: Simple walking animation with legs."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Walking Legs")
    print("="*60)
    print("Creating a body with legs for walking animation...")
    
    # Create skeleton
    skeleton = create_simple_skeleton()
    print(f"\nSkeleton hierarchy:")
    print(skeleton.get_hierarchy_string())
    
    # Create model
    model = RiggedModel("walking_body", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("torso", list(range(8)))
    
    # Create walking script
    script = BehaviorScript("walk")
    
    # Left leg forward
    script.rotate(x=30, duration=0.3, easing='ease_in_out', bone="left_hip")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="left_knee")
    
    # Right leg back
    script.rotate(x=-30, duration=0.3, easing='ease_in_out', bone="right_hip")
    script.rotate(x=-30, duration=0.2, easing='ease_in_out', bone="right_knee")
    
    # Reverse
    script.rotate(x=-60, duration=0.6, easing='ease_in_out', bone="left_hip")
    script.rotate(x=-60, duration=0.4, easing='ease_in_out', bone="left_knee")
    script.rotate(x=60, duration=0.6, easing='ease_in_out', bone="right_hip")
    script.rotate(x=60, duration=0.4, easing='ease_in_out', bone="right_knee")
    
    # Return to center
    script.rotate(x=30, duration=0.3, easing='ease_in_out', bone="left_hip")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="left_knee")
    script.rotate(x=-30, duration=0.3, easing='ease_in_out', bone="right_hip")
    script.rotate(x=-30, duration=0.2, easing='ease_in_out', bone="right_knee")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("\nAnimating walking...")
    frame_count = 0
    for frame in anim.stream_frames(script):
        frame_count += 1
        if frame_count % 20 == 0:
            print(f"  Frame {frame.frame_number}: time={frame.timestamp:.2f}s")
    
    print(f"Generated {frame_count} frames\n")


def example_full_body_dance():
    """Example: Complex multi-bone dance sequence."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Full Body Dance")
    print("="*60)
    print("Creating a full body with coordinated bone movements...")
    
    skeleton = create_simple_skeleton()
    model = RiggedModel("dancer", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("torso", list(range(8)))
    
    # Create complex dance sequence
    script = BehaviorScript("dance")
    
    # Raise both arms
    script.rotate(z=90, duration=0.5, easing='ease_out', bone="left_shoulder")
    script.rotate(z=-90, duration=0.5, easing='ease_out', bone="right_shoulder")
    
    # Nod head
    script.rotate(x=20, duration=0.3, easing='ease_in_out', bone="head")
    script.rotate(x=-20, duration=0.3, easing='ease_in_out', bone="head")
    
    # Bend elbows
    script.rotate(y=90, duration=0.4, easing='ease_in_out', bone="left_elbow")
    script.rotate(y=-90, duration=0.4, easing='ease_in_out', bone="right_elbow")
    
    # Twist torso
    script.rotate(y=30, duration=0.5, easing='ease_in_out', bone="torso")
    script.rotate(y=-60, duration=1.0, easing='ease_in_out', bone="torso")
    script.rotate(y=30, duration=0.5, easing='ease_in_out', bone="torso")
    
    # Lower arms
    script.rotate(z=-90, duration=0.5, easing='ease_in', bone="left_shoulder")
    script.rotate(z=90, duration=0.5, easing='ease_in', bone="right_shoulder")
    
    # Kick legs
    script.rotate(x=45, duration=0.3, easing='ease_out', bone="left_hip")
    script.rotate(x=-45, duration=0.3, easing='ease_in', bone="left_hip")
    script.rotate(x=45, duration=0.3, easing='ease_out', bone="right_hip")
    script.rotate(x=-45, duration=0.3, easing='ease_in', bone="right_hip")
    
    anim = AnimationSystem(model, width=1024, height=768, fps=30)
    
    print("\nAnimating dance...")
    frame_count = 0
    for frame in anim.stream_frames(script):
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"  Frame {frame.frame_number}: time={frame.timestamp:.2f}s")
    
    print(f"Generated {frame_count} frames\n")


def example_custom_skeleton():
    """Example: Create a custom skeleton with specific structure."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Skeleton")
    print("="*60)
    print("Creating a custom skeleton structure...")
    
    # Create custom skeleton - a simple tail
    skeleton = Skeleton("tail")
    skeleton.add_bone("base", position=np.array([0.0, 0.0, 0.0]))
    skeleton.add_bone("segment1", parent_name="base", 
                     position=np.array([0.0, 0.0, 1.0]))
    skeleton.add_bone("segment2", parent_name="segment1",
                     position=np.array([0.0, 0.0, 1.0]))
    skeleton.add_bone("segment3", parent_name="segment2",
                     position=np.array([0.0, 0.0, 1.0]))
    skeleton.add_bone("tip", parent_name="segment3",
                     position=np.array([0.0, 0.0, 1.0]))
    
    print(f"\nCustom skeleton hierarchy:")
    print(skeleton.get_hierarchy_string())
    print(f"Total bones: {len(skeleton.bones)}")
    
    # Create model
    model = RiggedModel("snake_tail", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("base", list(range(8)))
    
    # Animate - wave the tail
    script = BehaviorScript("tail_wave")
    
    # Wave motion through segments
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment1")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment2")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment3")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="tip")
    
    script.rotate(x=-60, duration=0.4, easing='ease_in_out', bone="segment1")
    script.rotate(x=-60, duration=0.4, easing='ease_in_out', bone="segment2")
    script.rotate(x=-60, duration=0.4, easing='ease_in_out', bone="segment3")
    script.rotate(x=-60, duration=0.4, easing='ease_in_out', bone="tip")
    
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment1")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment2")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="segment3")
    script.rotate(x=30, duration=0.2, easing='ease_in_out', bone="tip")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("\nAnimating tail wave...")
    frame_count = 0
    for frame in anim.stream_frames(script):
        frame_count += 1
        if frame_count % 15 == 0:
            print(f"  Frame {frame.frame_number}")
    
    print(f"Generated {frame_count} frames\n")


def example_hierarchy_effects():
    """Example: Demonstrate hierarchical bone transformations."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Hierarchical Transformations")
    print("="*60)
    print("Demonstrating parent-child bone relationships...")
    
    skeleton = create_arm_skeleton()
    model = RiggedModel("hierarchy_test", skeleton)
    model.set_cube_mesh()
    model.attach_vertices_to_bone("shoulder", list(range(8)))
    
    script = BehaviorScript("hierarchy")
    
    # Rotate shoulder - all children should follow
    print("\n1. Rotating shoulder (children will follow)...")
    script.rotate(y=90, duration=1.0, easing='linear', bone="shoulder")
    
    # Rotate elbow - only affects elbow and its children
    print("2. Rotating elbow (hand will follow)...")
    script.rotate(z=90, duration=1.0, easing='linear', bone="elbow")
    
    # Rotate hand - only affects hand
    print("3. Rotating hand (leaf node)...")
    script.rotate(x=180, duration=1.0, easing='linear', bone="hand")
    
    anim = AnimationSystem(model, width=800, height=600, fps=30)
    
    print("\nAnimating hierarchy...")
    frame_count = 0
    for frame in anim.stream_frames(script):
        frame_count += 1
    
    print(f"Generated {frame_count} frames")
    print("\nHierarchy demonstration complete!\n")


def main():
    """Run all rigged model examples."""
    print("\n" + "="*70)
    print("RIGGED MODEL ANIMATION EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate skeletal rigging and bone animations.")
    print("Each bone can be animated independently with hierarchical effects.")
    
    example_simple_arm()
    example_walking_legs()
    example_full_body_dance()
    example_custom_skeleton()
    example_hierarchy_effects()
    
    print("\n" + "="*70)
    print("ALL RIGGED MODEL EXAMPLES COMPLETE!")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Hierarchical bone structures")
    print("  ✓ Individual bone targeting in animations")
    print("  ✓ Parent-child transformation propagation")
    print("  ✓ Complex multi-bone choreography")
    print("  ✓ Custom skeleton creation")
    print("\nYou can now create complex rigged models with articulated parts!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
