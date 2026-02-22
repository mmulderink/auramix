"""
Example Usage of the Procedural Animation System
Demonstrates how to create animations and stream frames.
"""

from model import Model3D
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
import numpy as np


def example_basic_animation():
    """Basic example: Create a simple rotating cube animation."""
    print("=== Basic Animation Example ===")
    
    # 1. Create a 3D model (cube placeholder)
    model = Model3D(name="cube")
    
    # 2. Create behavior script
    script = BehaviorScript("rotate_cube")
    script.rotate(y=360, duration=2.0, easing='linear')
    
    # 3. Initialize animation system
    anim_system = AnimationSystem(model, width=800, height=600, fps=30)
    
    # 4. Stream frames
    print(f"Streaming animation frames...")
    frame_count = 0
    for frame in anim_system.stream_frames(script, max_frames=60):
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"  Frame {frame.frame_number}: time={frame.timestamp:.2f}s, "
                  f"rotation={frame.state.rotation}")
    
    print(f"Generated {frame_count} frames\n")


def example_complex_sequence():
    """Complex example: Multi-step animation sequence."""
    print("=== Complex Animation Sequence ===")
    
    model = Model3D(name="animated_cube")
    
    # Create complex behavior script
    script = BehaviorScript("complex_sequence")
    script.translate(x=3, duration=1.0, easing='ease_in_out')
    script.rotate(y=180, z=90, duration=1.5, easing='ease_in_out')
    script.scale(x=0.5, y=0.5, z=0.5, duration=0.5, easing='ease_out')
    script.translate(x=-3, y=2, duration=1.0, easing='ease_in_out')
    script.rotate(y=-180, z=-90, duration=1.0, easing='linear')
    
    anim_system = AnimationSystem(model, width=1920, height=1080, fps=60)
    
    print("Streaming complex animation...")
    frame_count = 0
    for frame in anim_system.stream_frames(script):
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"  Frame {frame.frame_number}: pos={frame.state.position}, "
                  f"rot={frame.state.rotation}, scale={frame.state.scale}")
    
    print(f"Generated {frame_count} frames\n")


def example_realtime_control():
    """Real-time control: Process individual commands."""
    print("=== Real-time Control Example ===")
    
    model = Model3D(name="controlled_cube")
    anim_system = AnimationSystem(model, width=800, height=600, fps=30)
    
    # Create individual transform commands
    from behavior_script import TransformCommand
    
    commands = [
        TransformCommand('translate', {'x': 2, 'y': 1}, duration=0.5, easing='linear'),
        TransformCommand('rotate', {'z': 45}, duration=0.3, easing='ease_in_out'),
        TransformCommand('scale', {'x': 1.5, 'y': 1.5, 'z': 1.5}, duration=0.4, easing='ease_out'),
    ]
    
    print("Processing real-time commands...")
    for i, cmd in enumerate(commands):
        print(f"\n  Processing command {i+1}: {cmd.transform_type}")
        
        # Process command until complete
        complete = False
        frame_count = 0
        while not complete:
            complete = anim_system.process_command(cmd, anim_system.frame_time)
            frame = anim_system.generate_frame()
            
            frame_count += 1
            if frame_count % 5 == 0:
                print(f"    Frame {frame.frame_number}: state updated")
            
            anim_system.update(anim_system.frame_time)
        
        print(f"  Command complete after {frame_count} frames")
    
    print(f"\nFinal state: pos={anim_system.current_state.position}, "
          f"rot={anim_system.current_state.rotation}, "
          f"scale={anim_system.current_state.scale}\n")


def example_state_management():
    """State management: Get and set model state."""
    print("=== State Management Example ===")
    
    model = Model3D(name="stateful_cube")
    anim_system = AnimationSystem(model)
    
    # Set initial state
    print("Setting initial state...")
    anim_system.set_state(
        position=np.array([1.0, 2.0, 3.0]),
        rotation=np.array([45.0, 30.0, 60.0]),
        scale=np.array([0.8, 0.8, 0.8])
    )
    
    state = anim_system.get_state()
    print(f"  Position: {state.position}")
    print(f"  Rotation: {state.rotation}")
    print(f"  Scale: {state.scale}")
    
    # Generate frame with current state
    frame = anim_system.get_current_frame()
    print(f"\nGenerated frame {frame.frame_number} with {len(frame.projected_vertices)} vertices")
    print(f"  Projected vertices shape: {frame.projected_vertices.shape}")
    print(f"  Number of faces: {len(frame.faces)}\n")


def example_frame_data():
    """Examine frame data structure."""
    print("=== Frame Data Structure ===")
    
    model = Model3D(name="data_cube")
    anim_system = AnimationSystem(model, width=1280, height=720, fps=24)
    
    script = BehaviorScript("sample")
    script.rotate(y=90, duration=1.0)
    
    # Get first frame
    frames = anim_system.stream_frames(script, max_frames=1)
    frame = next(frames)
    
    print(f"Frame #{frame.frame_number}")
    print(f"  Timestamp: {frame.timestamp}s")
    print(f"  Projected vertices (2D):")
    for i, vertex in enumerate(frame.projected_vertices[:3]):  # Show first 3
        print(f"    Vertex {i}: ({vertex[0]:.2f}, {vertex[1]:.2f})")
    print(f"  Total vertices: {len(frame.projected_vertices)}")
    print(f"  Faces: {len(frame.faces)} triangles")
    print(f"  Metadata: {frame.metadata}")
    print(f"  State: pos={frame.state.position}, rot={frame.state.rotation}\n")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("PROCEDURAL ANIMATION SYSTEM - EXAMPLES")
    print("="*60 + "\n")
    
    example_basic_animation()
    example_complex_sequence()
    example_realtime_control()
    example_state_management()
    example_frame_data()
    
    print("="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
