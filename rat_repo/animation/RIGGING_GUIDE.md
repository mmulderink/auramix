# Rigging System Guide

## Overview

The rigging system allows you to create articulated 3D models with hierarchical bone structures. Each bone can be animated independently, and parent bones affect their children.

## Quick Start

```python
from rigging import Skeleton
from model import RiggedModel
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
import numpy as np

# 1. Create skeleton
skeleton = Skeleton("character")
skeleton.add_bone("root")
skeleton.add_bone("upper_arm", parent_name="root", 
                 position=np.array([0, 0, 0]))
skeleton.add_bone("lower_arm", parent_name="upper_arm",
                 position=np.array([2, 0, 0]))

# 2. Create rigged model
model = RiggedModel("my_character", skeleton)
model.set_cube_mesh()  # Or set custom mesh

# 3. Attach vertices to bones
model.attach_vertices_to_bone("root", [0, 1, 2, 3])
model.attach_vertices_to_bone("upper_arm", [4, 5, 6, 7])

# 4. Create animation targeting specific bones
script = BehaviorScript("wave")
script.rotate(z=45, duration=1.0, bone="upper_arm")
script.rotate(y=90, duration=1.0, bone="lower_arm")

# 5. Animate
anim = AnimationSystem(model, width=800, height=600, fps=30)
for frame in anim.stream_frames(script):
    process_frame(frame)
```

## Core Concepts

### Bones

Bones are the basic building blocks of a skeleton. Each bone has:
- **Name**: Unique identifier
- **Parent**: Optional parent bone (None for root bones)
- **Children**: List of child bones
- **Local Transform**: Position, rotation, scale relative to parent
- **Bind Pose**: Initial offset from parent
- **Vertex Weights**: Which vertices this bone influences

### Hierarchy

Bones form a parent-child tree:
```
root
  ├─ head
  ├─ left_arm
  │   └─ left_hand
  └─ right_arm
      └─ right_hand
```

When you transform a parent, all children inherit that transformation.

### Skinning

Skinning determines how bones affect vertices:
- Each vertex can be influenced by one or more bones
- Weights determine how much each bone affects each vertex
- Weights for each vertex sum to 1.0

## Skeleton Creation

### Manual Creation

```python
from rigging import Skeleton
import numpy as np

skeleton = Skeleton("my_skeleton")

# Add root bone
skeleton.add_bone("torso")

# Add child bones with positions
skeleton.add_bone("head", parent_name="torso",
                 position=np.array([0, 2, 0]))  # 2 units up

skeleton.add_bone("left_arm", parent_name="torso",
                 position=np.array([-1.5, 1.5, 0]))

skeleton.add_bone("left_elbow", parent_name="left_arm",
                 position=np.array([-1, 0, 0]))

# View hierarchy
print(skeleton.get_hierarchy_string())
```

### Using Presets

```python
from rigging import create_simple_skeleton, create_arm_skeleton

# Simple humanoid body
skeleton = create_simple_skeleton()

# Just an arm
arm = create_arm_skeleton()
```

### Dynamic Creation

```python
# Create a chain (tail, tentacle, etc.)
skeleton = Skeleton("chain")
skeleton.add_bone("base")

for i in range(10):
    parent = f"segment{i-1}" if i > 0 else "base"
    skeleton.add_bone(f"segment{i}", 
                     parent_name=parent,
                     position=np.array([0, 0, 1]))
```

## Bone Operations

### Get Bone
```python
bone = skeleton.get_bone("left_arm")
```

### Transform Bone
```python
import numpy as np

bone = skeleton.get_bone("left_arm")
bone.set_position(np.array([1, 2, 3]))
bone.set_rotation(np.array([45, 0, 0]))  # Degrees
bone.set_scale(np.array([1.5, 1.5, 1.5]))
```

### Query Bone Info
```python
depth = bone.get_depth()  # Depth in hierarchy
root = bone.get_root()    # Get root bone
descendants = bone.get_descendants()  # Get all children recursively
```

## Rigged Models

### Creating Rigged Models

```python
from model import RiggedModel

model = RiggedModel("character", skeleton)
```

### Setting Mesh

```python
import numpy as np

# Custom vertices and faces
vertices = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    # ... more vertices
])

faces = [
    (0, 1, 2), (0, 2, 3),  # Triangle indices
    # ... more faces
]

model.set_mesh(vertices, faces)

# Or use cube placeholder
model.set_cube_mesh()
```

### Attaching Vertices to Bones

```python
# Attach specific vertices with equal weights
model.attach_vertices_to_bone("torso", [0, 1, 2, 3, 4, 5, 6, 7])

# Attach with custom weights
model.attach_vertices_to_bone("head", 
                             vertex_indices=[8, 9, 10, 11],
                             weights=[1.0, 0.8, 0.8, 1.0])

# Auto-weight all vertices based on distance
model.auto_weight_vertices()
```

## Bone-Targeted Animations

### Basic Bone Animation

```python
script = BehaviorScript("arm_wave")

# Target specific bone with 'bone=' parameter
script.rotate(z=45, duration=1.0, bone="upper_arm")
script.translate(y=2, duration=0.5, bone="hand")
script.scale(x=1.5, y=1.5, z=1.5, duration=0.5, bone="head")
```

### Coordinated Movement

```python
script = BehaviorScript("dance")

# Move multiple bones in sequence
script.rotate(z=90, duration=0.5, bone="left_arm")
script.rotate(z=-90, duration=0.5, bone="right_arm")
script.rotate(x=20, duration=0.3, bone="head")
script.rotate(y=90, duration=0.5, bone="left_elbow")
```

### Hierarchical Effects

When you transform a parent bone, all children are affected:

```python
# Rotating shoulder affects elbow, wrist, and hand
script.rotate(y=90, duration=1.0, bone="shoulder")

# Rotating elbow affects wrist and hand (but not shoulder)
script.rotate(z=45, duration=0.5, bone="elbow")
```

## Advanced Techniques

### Walking Animation

```python
script = BehaviorScript("walk")

# Alternating legs
script.rotate(x=30, duration=0.4, bone="left_hip")
script.rotate(x=-30, duration=0.4, bone="right_hip")

script.rotate(x=-60, duration=0.8, bone="left_hip")
script.rotate(x=60, duration=0.8, bone="right_hip")

# Opposite arm swing
script.rotate(z=25, duration=0.4, bone="right_shoulder")
script.rotate(z=-25, duration=0.4, bone="left_shoulder")
```

### Wave Motion (Chain/Tail)

```python
script = BehaviorScript("wave")

# Wave going down the chain
for i in range(5):
    script.rotate(x=30, duration=0.15, bone=f"segment{i}")

# Reverse wave
for i in range(5):
    script.rotate(x=-60, duration=0.3, bone=f"segment{i}")

# Back to center
for i in range(5):
    script.rotate(x=30, duration=0.15, bone=f"segment{i}")
```

### Multi-Bone Gesture

```python
script = BehaviorScript("gesture")

# Raise arms
script.rotate(z=80, duration=0.6, bone="left_shoulder")
script.rotate(z=-80, duration=0.6, bone="right_shoulder")

# Bend elbows
script.rotate(y=90, duration=0.5, bone="left_elbow")
script.rotate(y=-90, duration=0.5, bone="right_elbow")

# Nod head
script.rotate(x=20, duration=0.3, bone="head")
script.rotate(x=-20, duration=0.3, bone="head")

# Lower arms
script.rotate(y=-90, duration=0.5, bone="left_elbow")
script.rotate(y=90, duration=0.5, bone="right_elbow")
script.rotate(z=-80, duration=0.6, bone="left_shoulder")
script.rotate(z=80, duration=0.6, bone="right_shoulder")
```

## Best Practices

### 1. Plan Your Hierarchy

Design your skeleton hierarchy before creating bones:
```
         root/torso
            /    \
        head    arms/legs
                  |
              hands/feet
```

### 2. Use Descriptive Names

```python
# Good
skeleton.add_bone("left_shoulder")
skeleton.add_bone("right_knee")

# Avoid
skeleton.add_bone("bone1")
skeleton.add_bone("b2")
```

### 3. Bind Pose Matters

Set bind positions to match the initial model pose:
```python
# Arm extends to the side
skeleton.add_bone("shoulder", position=np.array([0, 1.5, 0]))
skeleton.add_bone("elbow", parent_name="shoulder",
                 position=np.array([2, 0, 0]))  # 2 units to the side
```

### 4. Test Incrementally

Test each bone's range of motion:
```python
# Test one bone at a time
script.rotate(y=90, duration=1.0, bone="shoulder")
# Verify it looks right before adding more
```

### 5. Use Easing for Natural Motion

```python
# Quick start, smooth finish
script.rotate(z=45, duration=1.0, easing='ease_out', bone="arm")

# Smooth start, quick finish
script.rotate(z=-45, duration=1.0, easing='ease_in', bone="arm")

# Smooth both ends (most natural)
script.rotate(z=45, duration=1.0, easing='ease_in_out', bone="arm")
```

## Common Patterns

### Breathing Animation
```python
script = BehaviorScript("breathe")
for _ in range(3):
    script.scale(y=1.1, duration=1.0, easing='ease_in_out', bone="torso")
    script.scale(y=1.0, duration=1.0, easing='ease_in_out', bone="torso")
```

### Look Around
```python
script = BehaviorScript("look")
script.rotate(y=45, duration=0.5, easing='ease_in_out', bone="head")
script.rotate(y=-90, duration=1.0, easing='ease_in_out', bone="head")
script.rotate(y=45, duration=0.5, easing='ease_in_out', bone="head")
```

### Point Gesture
```python
script = BehaviorScript("point")
script.rotate(z=-90, duration=0.5, easing='ease_out', bone="right_shoulder")
script.rotate(y=-90, duration=0.3, easing='ease_in_out', bone="right_elbow")
```

## Troubleshooting

### Vertices Not Moving

Make sure vertices are attached to bones:
```python
model.attach_vertices_to_bone("bone_name", vertex_indices)
# Or
model.auto_weight_vertices()
```

### Unexpected Transformations

Check the bone hierarchy - child bones inherit parent transforms:
```python
print(skeleton.get_hierarchy_string())
```

### Bones Not Found

Verify bone names:
```python
print(skeleton.get_bone_names())
```

### Model Needs Recalculation

Mark model as dirty after manual bone changes:
```python
bone.set_rotation(np.array([45, 0, 0]))
model.mark_dirty()
```

## Examples

Run these to see rigging in action:

```bash
# Text examples
python rigged_examples.py

# Visual examples
python test_rigged_visual.py       # Quick test
python rigged_visual_demo.py       # Full demo suite
```

## API Reference

### Skeleton
- `add_bone(name, parent_name, position, rotation)` - Add bone to skeleton
- `get_bone(name)` - Get bone by name
- `remove_bone(name)` - Remove bone
- `get_all_bones()` - Get all bones
- `get_bone_names()` - Get all bone names
- `reset_pose()` - Reset all bones to bind pose
- `get_hierarchy_string()` - Get visual hierarchy representation

### Bone
- `set_position(position)` - Set local position
- `set_rotation(rotation)` - Set local rotation (degrees)
- `set_scale(scale)` - Set local scale
- `get_local_matrix()` - Get local transform matrix
- `get_world_matrix()` - Get world transform matrix
- `add_child(bone)` - Add child bone
- `get_depth()` - Get depth in hierarchy
- `get_descendants()` - Get all descendant bones

### RiggedModel
- `set_mesh(vertices, faces)` - Set mesh geometry
- `set_cube_mesh()` - Set placeholder cube mesh
- `attach_vertices_to_bone(bone_name, indices, weights)` - Attach vertices
- `auto_weight_vertices()` - Auto-assign vertex weights
- `get_transformed_vertices()` - Get current pose vertices
- `mark_dirty()` - Mark for recalculation
- `reset_pose()` - Reset to bind pose
- `get_bone(name)` - Get bone by name

### BehaviorScript (with bone targeting)
- `translate(x, y, z, duration, easing, bone)` - Translate bone
- `rotate(x, y, z, duration, easing, bone)` - Rotate bone
- `scale(x, y, z, duration, easing, bone)` - Scale bone
- `composed(transforms, duration, easing, bone)` - Composed transform

All transform methods accept optional `bone="bone_name"` parameter to target specific bones.
