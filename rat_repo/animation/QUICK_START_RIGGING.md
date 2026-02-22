# Quick Reference: Rigged Model Animation

## 30-Second Start

```python
from rigging import Skeleton
from model import RiggedModel
from behavior_script import BehaviorScript
from animation_system import AnimationSystem
import numpy as np

# Create skeleton
skeleton = Skeleton("char")
skeleton.add_bone("root")
skeleton.add_bone("arm", "root", position=np.array([1, 0, 0]))

# Create model
model = RiggedModel("char", skeleton)
model.set_cube_mesh()
model.attach_vertices_to_bone("root", list(range(8)))

# Animate specific bone
script = BehaviorScript("wave")
script.rotate(z=45, duration=1.0, bone="arm")

# Run
anim = AnimationSystem(model, width=800, height=600, fps=30)
for frame in anim.stream_frames(script):
    pass  # Process frame
```

## Bone Animation Methods

```python
# All these methods accept bone="bone_name" parameter

script.translate(x=2, y=1, z=0, duration=1.0, bone="arm")
script.rotate(x=45, y=90, z=0, duration=1.0, bone="elbow")
script.scale(x=1.5, y=1.5, z=1.5, duration=0.5, bone="hand")
script.composed(transforms=[...], duration=1.0, bone="head")
```

## Common Skeleton Patterns

### Arm Chain
```python
skeleton.add_bone("shoulder")
skeleton.add_bone("elbow", "shoulder", position=np.array([2, 0, 0]))
skeleton.add_bone("wrist", "elbow", position=np.array([2, 0, 0]))
skeleton.add_bone("hand", "wrist", position=np.array([1, 0, 0]))
```

### Spine/Tail Chain
```python
skeleton.add_bone("base")
for i in range(10):
    parent = f"seg{i-1}" if i > 0 else "base"
    skeleton.add_bone(f"seg{i}", parent, position=np.array([0, 0, 1]))
```

### Humanoid Core
```python
skeleton.add_bone("torso")
skeleton.add_bone("head", "torso", position=np.array([0, 2, 0]))
skeleton.add_bone("left_arm", "torso", position=np.array([-1.5, 1.5, 0]))
skeleton.add_bone("right_arm", "torso", position=np.array([1.5, 1.5, 0]))
```

## Animation Recipes

### Wave
```python
script.rotate(z=30, duration=0.5, easing='ease_in_out', bone="arm")
script.rotate(z=-60, duration=1.0, easing='ease_in_out', bone="arm")
script.rotate(z=30, duration=0.5, easing='ease_in_out', bone="arm")
```

### Bend
```python
script.rotate(y=90, duration=0.5, easing='ease_in_out', bone="elbow")
script.rotate(y=-90, duration=0.5, easing='ease_in_out', bone="elbow")
```

### Nod
```python
script.rotate(x=20, duration=0.3, easing='ease_in_out', bone="head")
script.rotate(x=-20, duration=0.3, easing='ease_in_out', bone="head")
```

### Walk Cycle (Legs)
```python
script.rotate(x=30, duration=0.4, bone="left_leg")
script.rotate(x=-30, duration=0.4, bone="right_leg")
script.rotate(x=-60, duration=0.8, bone="left_leg")
script.rotate(x=60, duration=0.8, bone="right_leg")
```

## Key Points

✓ **Hierarchy Matters**: Parent transforms affect all children
✓ **Bone Names**: Use descriptive names ("left_arm", not "bone1")
✓ **Bind Pose**: Set bone positions to match initial model
✓ **Vertex Weights**: Attach vertices to bones or use `auto_weight_vertices()`
✓ **Target Bones**: Add `bone="name"` to transform methods
✓ **Easing**: Use 'ease_in_out' for most natural motion

## Useful Commands

```python
# View skeleton structure
print(skeleton.get_hierarchy_string())

# List all bones
print(skeleton.get_bone_names())

# Get bone
bone = skeleton.get_bone("arm")

# Manual bone control
bone.set_rotation(np.array([45, 0, 0]))
model.mark_dirty()

# Reset everything
skeleton.reset_pose()
model.reset_pose()
```

## Run Examples

```bash
python rigged_examples.py          # Text output
python test_rigged_visual.py       # Quick visual test
python rigged_visual_demo.py       # Full visual demo suite
```

## Full Documentation

See `RIGGING_GUIDE.md` for complete documentation.
