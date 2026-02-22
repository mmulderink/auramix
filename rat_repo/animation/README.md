# Procedural 3D Animation System

A real-time 3D-to-2D animation generation system with **skeletal rigging**, state management, and transformation sequencing.

## Overview

This system generates procedural animations by:
1. Managing 3D model state (position, rotation, scale) and **rigged skeletons**
2. Processing transformation commands from behavior scripts **targeting specific bones**
3. Projecting 3D models to 2D screen space
4. Streaming animation frames in real-time

**NEW**: Full skeletal rigging system with hierarchical bone animations!

## Quick Start

### Simple Model
```python
from model import Model3D
from behavior_script import BehaviorScript
from animation_system import AnimationSystem

model = Model3D("cube")
script = BehaviorScript("spin")
script.rotate(y=360, duration=2.0)
anim = AnimationSystem(model, width=800, height=600, fps=30)

for frame in anim.stream_frames(script):
    process_frame(frame)
```

### Rigged Model
```python
from rigging import Skeleton
from model import RiggedModel
import numpy as np

# Create skeleton
skeleton = Skeleton("character")
skeleton.add_bone("torso")
skeleton.add_bone("arm", "torso", position=np.array([1.5, 0, 0]))

# Create rigged model
model = RiggedModel("character", skeleton)
model.set_cube_mesh()
model.attach_vertices_to_bone("torso", [0, 1, 2, 3])

# Animate specific bones
script = BehaviorScript("wave")
script.rotate(z=45, duration=1.0, bone="arm")  # Target specific bone!

anim = AnimationSystem(model, width=800, height=600, fps=30)
for frame in anim.stream_frames(script):
    process_frame(frame)
```

**See [QUICK_START_RIGGING.md](QUICK_START_RIGGING.md) for rigging quick reference**

## Architecture

### Core Components

```
┌─────────────────┐
│   model.py      │  ← 3D Model Definition (placeholder)
└─────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   animation_system.py           │  ← Main Animation Engine
│  ┌─────────────────────────┐    │
│  │  AnimationSystem        │    │
│  │  - State Management     │    │
│  │  - Transform Processing │    │
│  │  - Frame Generation     │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │  TransformationEngine   │    │
│  │  - Matrix Operations    │    │
│  │  - Easing Functions     │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │  ProjectionEngine       │    │
│  │  - 3D → 2D Projection   │    │
│  │  - Perspective Camera   │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
         ▲
         │
┌─────────────────┐
│ behavior_script │  ← Animation Sequencer (placeholder)
└─────────────────┘
```

### Files

- **`model.py`**: 3D model placeholder - defines geometry (currently a cube) and rigged models
- **`rigging.py`**: Skeletal rigging system with hierarchical bones
- **`behavior_script.py`**: Animation driver placeholder - defines transformation sequences with bone targeting
- **`animation_system.py`**: Core animation engine with state management for both simple and rigged models
- **`renderer.py`**: Visual rendering system for displaying animations in windows
- **`example_usage.py`**: Usage examples and demonstrations (text output)
- **`visual_demo.py`**: Visual animation demos (graphical output)
- **`rigged_examples.py`**: Rigged model animation examples (text output)
- **`rigged_visual_demo.py`**: Rigged model visual demos (graphical output)
- **`test_visual.py`**: Quick visual test script

## Features

### ✅ State Management
- Persistent state between transformation calls
- Position, rotation (Euler angles), and scale tracking
- State snapshots and restoration

### ✅ Rigging & Skeletal Animation
- **Hierarchical bone structures** with parent-child relationships
- **Individual bone targeting** - animate specific parts independently
- **Vertex skinning** - vertices influenced by bones with weights
- **Custom skeletons** - create any bone hierarchy you need
- **Automatic weight painting** - distance-based vertex assignment
- **Transformation propagation** - parent transforms affect children

### ✅ Transformation System
- **Translate**: Move objects in 3D space
- **Rotate**: Rotate around X, Y, Z axes (Euler angles)
- **Scale**: Non-uniform scaling
- **Composed**: Apply multiple transforms together
- **Bone-targeted**: Apply transformations to specific bones

### ✅ Animation Control
- Duration-based animations
- Easing functions (linear, ease-in, ease-out, ease-in-out, cubic variants)
- Real-time frame streaming
- Sequential command processing

### ✅ 3D-to-2D Projection
- Perspective projection with configurable FOV
- Customizable resolution and aspect ratio
- Camera distance control

## Usage

### Basic Animation (Simple Model)

```python
from model import Model3D
from behavior_script import BehaviorScript
from animation_system import AnimationSystem

# Create model
model = Model3D(name="cube")

# Create animation script
script = BehaviorScript("my_animation")
script.rotate(y=360, duration=2.0, easing='linear')
script.translate(x=5, duration=1.0, easing='ease_in_out')

# Initialize animation system
anim = AnimationSystem(model, width=800, height=600, fps=30)

# Stream frames
for frame in anim.stream_frames(script):
    # frame.projected_vertices contains 2D coordinates
    # frame.faces contains triangle indices
    # frame.state contains current 3D state
    process_frame(frame)
```

### Rigged Model Animation

```python
from rigging import Skeleton
from model import RiggedModel
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
import numpy as np

# Create skeleton
skeleton = Skeleton("character")
skeleton.add_bone("torso")
skeleton.add_bone("head", parent_name="torso", 
                 position=np.array([0, 2, 0]))
skeleton.add_bone("left_arm", parent_name="torso",
                 position=np.array([-1.5, 1.5, 0]))
skeleton.add_bone("left_elbow", parent_name="left_arm",
                 position=np.array([-1, 0, 0]))

# Create rigged model
model = RiggedModel("character", skeleton)
model.set_cube_mesh()  # Or set custom mesh

# Attach vertices to bones (or use auto_weight_vertices())
model.attach_vertices_to_bone("torso", [0, 1, 2, 3])
model.attach_vertices_to_bone("left_arm", [4, 5, 6, 7])

# Create animation targeting specific bones
script = BehaviorScript("wave")
script.rotate(z=45, duration=0.5, bone="left_arm")  # Rotate just the arm
script.rotate(z=-45, duration=0.5, bone="left_arm")
script.rotate(y=90, duration=0.5, bone="left_elbow")  # Bend the elbow
script.rotate(x=20, duration=0.3, bone="head")  # Nod the head

# Animate
anim = AnimationSystem(model, width=800, height=600, fps=30)
for frame in anim.stream_frames(script):
    process_frame(frame)
```

### Real-time Command Processing

```python
from behavior_script import TransformCommand

anim = AnimationSystem(model)

# Process individual commands
cmd = TransformCommand('rotate', {'y': 90}, duration=1.0)

while not anim.process_command(cmd, anim.frame_time):
    frame = anim.generate_frame()
    render(frame)
    anim.update(anim.frame_time)
```

### State Management

```python
import numpy as np

# Set state manually
anim.set_state(
    position=np.array([1.0, 2.0, 3.0]),
    rotation=np.array([45.0, 30.0, 0.0]),
    scale=np.array([1.5, 1.5, 1.5])
)

# Get current state
state = anim.get_state()
print(f"Position: {state.position}")
print(f"Rotation: {state.rotation}")
print(f"Scale: {state.scale}")
```

## Transformation Types

### Translate
```python
script.translate(x=2.0, y=1.0, z=-3.0, duration=1.0, easing='ease_in_out')

# Or target a specific bone
script.translate(x=2.0, duration=1.0, bone="left_arm")
```

### Rotate
```python
script.rotate(x=45, y=90, z=30, duration=2.0, easing='linear')  # Degrees

# Or target a specific bone
script.rotate(y=90, duration=1.0, bone="elbow")
```

### Scale
```python
script.scale(x=2.0, y=2.0, z=2.0, duration=0.5, easing='ease_out')

# Or target a specific bone
script.scale(x=1.5, y=1.5, z=1.5, duration=0.5, bone="hand")
```

### Composed
```python
script.composed(
    transforms=[
        {'type': 'translate', 'x': 5},
        {'type': 'rotate', 'y': 360},
        {'type': 'scale', 'x': 0.5, 'y': 0.5, 'z': 0.5}
    ],
    duration=3.0,
    easing='ease_in_out'
)

# Or target a specific bone
script.composed(
    transforms=[
        {'type': 'rotate', 'x': 45},
        {'type': 'translate', 'y': 2}
    ],
    duration=1.0,
    bone="head"
)
```

## Easing Functions

Available easing functions:
- `linear`
- `ease_in` (quadratic)
- `ease_out` (quadratic)
- `ease_in_out` (smooth start and end)
- `ease_in_cubic`
- `ease_out_cubic`

## Frame Data Structure

Each generated frame contains:

```python
@dataclass
class Frame2D:
    frame_number: int                    # Sequential frame index
    timestamp: float                     # Time in seconds
    projected_vertices: np.ndarray       # 2D coordinates (Nx2)
    faces: List[Tuple[int, int, int]]   # Triangle face indices
    state: ModelState                    # Current 3D state
    metadata: Dict[str, Any]            # Width, height, fps, etc.
```

## Examples

### Text-Based Examples

Run the examples to see the system in action:

```bash
python example_usage.py
```

This demonstrates:
- Basic rotating cube animation
- Complex multi-step sequences
- Real-time command processing
- State management
- Frame data inspection

### Visual Examples

Run the visual demos to see animations in a window:

```bash
python test_visual.py              # Quick spinning cube test
python visual_demo.py               # Full demo suite (6 animations)
python rigged_examples.py           # Rigged model examples (text)
python rigged_visual_demo.py        # Rigged model demos (visual - 6 animations)
```

## Future Expansion

### Model Placeholder (`model.py`)
Will be expanded with:
- Custom geometry loading (OBJ, FBX, etc.)
- Procedural shape generation (spheres, cylinders, custom meshes)
- Vertex colors and textures
- Advanced skinning (multi-bone influences per vertex)
- Inverse kinematics (IK)

### Behavior Script Placeholder (`behavior_script.py`)
Will be enhanced with:
- Keyframe interpolation
- Physics simulation hooks
- Procedural animation patterns
- Event-driven behaviors
- Looping and conditional logic
- Animation blending

### Rigging System (`rigging.py`)
Future enhancements:
- Constraints (look-at, parent, track-to)
- FK/IK switching
- Spline IK for tails/tentacles
- Animation retargeting
- Pose libraries

## Visual Output

### Quick Visual Test

```bash
python test_visual.py
```

This opens a window showing a spinning cube animation - perfect for testing the system!

### Full Visual Demos

```bash
python visual_demo.py
```

This runs 6 different animation demos:
1. **Spinning Cube** - Simple rotation
2. **Complex Movement** - Multi-step choreography
3. **Orbital Motion** - Composed transformations
4. **Pulsing Effect** - Scale animation
5. **Looping Animation** - Repeated sequences
6. **Ultimate Showcase** - Complete feature demo

### Using the Renderer in Code

```python
from renderer import AnimationPlayer, quick_preview

# Quick preview (easiest method)
quick_preview(anim_system, script, title="My Animation")

# Or use AnimationPlayer for more control
player = AnimationPlayer(anim_system, title="Custom Player")
player.play(script)
player.play_loop(script, iterations=3)  # Loop 3 times
```

### Renderer Features

- **Real-time playback** at specified FPS
- **On-screen info display** showing frame number, time, position, rotation, scale, FPS
- **Wireframe rendering** with customizable colors
- **Vertex visualization** (optional)
- **Loop support** for repeating animations
- **Frame saving** to image files

## Requirements

```
numpy>=1.20.0
matplotlib>=3.3.0
```

Install with:
```bash
pip install -r requirements.txt
```

## License

MIT License - Free to use and modify.
