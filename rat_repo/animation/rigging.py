"""
Rigging System
Hierarchical bone/joint system for articulated model animation.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Bone:
    """
    Represents a bone/joint in a rigged model.
    Bones form a hierarchy with parent-child relationships.
    """
    name: str
    parent: Optional['Bone'] = None
    children: List['Bone'] = field(default_factory=list)
    
    # Local transformation (relative to parent)
    local_position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    local_rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))  # Euler angles
    local_scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    
    # Bind pose (initial offset from parent)
    bind_position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    bind_rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    
    # Vertex indices influenced by this bone
    vertex_indices: List[int] = field(default_factory=list)
    vertex_weights: List[float] = field(default_factory=list)
    
    # Cached world transformation
    _world_matrix: Optional[np.ndarray] = None
    _dirty: bool = True
    
    def add_child(self, child: 'Bone'):
        """Add a child bone."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child.mark_dirty()
    
    def remove_child(self, child: 'Bone'):
        """Remove a child bone."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            child.mark_dirty()
    
    def mark_dirty(self):
        """Mark this bone and all children as needing recalculation."""
        self._dirty = True
        for child in self.children:
            child.mark_dirty()
    
    def set_position(self, position: np.ndarray):
        """Set local position."""
        self.local_position = position.copy()
        self.mark_dirty()
    
    def set_rotation(self, rotation: np.ndarray):
        """Set local rotation."""
        self.local_rotation = rotation.copy()
        self.mark_dirty()
    
    def set_scale(self, scale: np.ndarray):
        """Set local scale."""
        self.local_scale = scale.copy()
        self.mark_dirty()
    
    def get_local_matrix(self) -> np.ndarray:
        """Get local transformation matrix."""
        try:
            from .animation_system import TransformationEngine
        except ImportError:
            from animation_system import TransformationEngine
        
        # Combine bind pose with current transformation
        total_position = self.bind_position + self.local_position
        total_rotation = self.bind_rotation + self.local_rotation
        
        T = TransformationEngine.translation_matrix(*total_position)
        Rx = TransformationEngine.rotation_matrix_x(total_rotation[0])
        Ry = TransformationEngine.rotation_matrix_y(total_rotation[1])
        Rz = TransformationEngine.rotation_matrix_z(total_rotation[2])
        S = TransformationEngine.scale_matrix(*self.local_scale)
        
        return T @ Rz @ Ry @ Rx @ S
    
    def get_world_matrix(self, force_recalc: bool = False) -> np.ndarray:
        """Get world transformation matrix (includes parent transforms)."""
        if not self._dirty and self._world_matrix is not None and not force_recalc:
            return self._world_matrix
        
        local_matrix = self.get_local_matrix()
        
        if self.parent is None:
            self._world_matrix = local_matrix
        else:
            parent_world = self.parent.get_world_matrix()
            self._world_matrix = parent_world @ local_matrix
        
        self._dirty = False
        return self._world_matrix
    
    def attach_vertices(self, indices: List[int], weights: Optional[List[float]] = None):
        """Attach vertices to this bone with optional weights."""
        self.vertex_indices = indices
        if weights is None:
            self.vertex_weights = [1.0] * len(indices)
        else:
            self.vertex_weights = weights
    
    def get_depth(self) -> int:
        """Get depth in hierarchy (root = 0)."""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1
    
    def get_root(self) -> 'Bone':
        """Get root bone."""
        if self.parent is None:
            return self
        return self.parent.get_root()
    
    def get_descendants(self) -> List['Bone']:
        """Get all descendant bones."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def __repr__(self):
        return f"Bone('{self.name}', children={len(self.children)}, vertices={len(self.vertex_indices)})"


class Skeleton:
    """
    Manages a hierarchy of bones for rigged models.
    """
    
    def __init__(self, name: str = "skeleton"):
        self.name = name
        self.bones: Dict[str, Bone] = {}
        self.root_bones: List[Bone] = []
    
    def add_bone(self, name: str, parent_name: Optional[str] = None,
                 position: Optional[np.ndarray] = None,
                 rotation: Optional[np.ndarray] = None) -> Bone:
        """Add a bone to the skeleton."""
        if name in self.bones:
            raise ValueError(f"Bone '{name}' already exists")
        
        bone = Bone(name=name)
        
        if position is not None:
            bone.bind_position = position.copy()
        if rotation is not None:
            bone.bind_rotation = rotation.copy()
        
        if parent_name is not None:
            if parent_name not in self.bones:
                raise ValueError(f"Parent bone '{parent_name}' not found")
            parent = self.bones[parent_name]
            parent.add_child(bone)
        else:
            self.root_bones.append(bone)
        
        self.bones[name] = bone
        return bone
    
    def get_bone(self, name: str) -> Optional[Bone]:
        """Get bone by name."""
        return self.bones.get(name)
    
    def remove_bone(self, name: str):
        """Remove a bone from the skeleton."""
        if name not in self.bones:
            return
        
        bone = self.bones[name]
        
        # Remove from parent
        if bone.parent:
            bone.parent.remove_child(bone)
        else:
            if bone in self.root_bones:
                self.root_bones.remove(bone)
        
        # Orphan children
        for child in bone.children[:]:
            bone.remove_child(child)
            self.root_bones.append(child)
        
        del self.bones[name]
    
    def get_all_bones(self) -> List[Bone]:
        """Get all bones in the skeleton."""
        return list(self.bones.values())
    
    def get_bone_names(self) -> List[str]:
        """Get names of all bones."""
        return list(self.bones.keys())
    
    def reset_pose(self):
        """Reset all bones to their bind pose."""
        for bone in self.bones.values():
            bone.local_position = np.array([0.0, 0.0, 0.0])
            bone.local_rotation = np.array([0.0, 0.0, 0.0])
            bone.local_scale = np.array([1.0, 1.0, 1.0])
            bone.mark_dirty()
    
    def get_hierarchy_string(self) -> str:
        """Get a string representation of the bone hierarchy."""
        lines = []
        
        def add_bone_lines(bone: Bone, indent: int = 0):
            prefix = "  " * indent + ("└─ " if indent > 0 else "")
            lines.append(f"{prefix}{bone.name}")
            for child in bone.children:
                add_bone_lines(child, indent + 1)
        
        for root in self.root_bones:
            add_bone_lines(root)
        
        return "\n".join(lines)
    
    def copy(self) -> 'Skeleton':
        """Create a deep copy of the skeleton."""
        new_skeleton = Skeleton(self.name)
        
        # Copy bones in hierarchical order
        def copy_bone_hierarchy(bone: Bone, parent_name: Optional[str] = None):
            new_bone = new_skeleton.add_bone(
                bone.name,
                parent_name,
                bone.bind_position,
                bone.bind_rotation
            )
            new_bone.local_position = bone.local_position.copy()
            new_bone.local_rotation = bone.local_rotation.copy()
            new_bone.local_scale = bone.local_scale.copy()
            new_bone.vertex_indices = bone.vertex_indices.copy()
            new_bone.vertex_weights = bone.vertex_weights.copy()
            
            for child in bone.children:
                copy_bone_hierarchy(child, bone.name)
        
        for root in self.root_bones:
            copy_bone_hierarchy(root)
        
        return new_skeleton
    
    def __repr__(self):
        return f"Skeleton('{self.name}', bones={len(self.bones)}, roots={len(self.root_bones)})"


def create_simple_skeleton() -> Skeleton:
    """Create a simple example skeleton (body with limbs)."""
    skeleton = Skeleton("simple_body")
    
    # Root bone (torso)
    skeleton.add_bone("torso", position=np.array([0.0, 0.0, 0.0]))
    
    # Head
    skeleton.add_bone("head", parent_name="torso", 
                     position=np.array([0.0, 2.0, 0.0]))
    
    # Left arm
    skeleton.add_bone("left_shoulder", parent_name="torso",
                     position=np.array([-1.5, 1.5, 0.0]))
    skeleton.add_bone("left_elbow", parent_name="left_shoulder",
                     position=np.array([-1.0, 0.0, 0.0]))
    skeleton.add_bone("left_hand", parent_name="left_elbow",
                     position=np.array([-1.0, 0.0, 0.0]))
    
    # Right arm
    skeleton.add_bone("right_shoulder", parent_name="torso",
                     position=np.array([1.5, 1.5, 0.0]))
    skeleton.add_bone("right_elbow", parent_name="right_shoulder",
                     position=np.array([1.0, 0.0, 0.0]))
    skeleton.add_bone("right_hand", parent_name="right_elbow",
                     position=np.array([1.0, 0.0, 0.0]))
    
    # Left leg
    skeleton.add_bone("left_hip", parent_name="torso",
                     position=np.array([-0.5, -0.5, 0.0]))
    skeleton.add_bone("left_knee", parent_name="left_hip",
                     position=np.array([0.0, -1.5, 0.0]))
    skeleton.add_bone("left_foot", parent_name="left_knee",
                     position=np.array([0.0, -1.5, 0.0]))
    
    # Right leg
    skeleton.add_bone("right_hip", parent_name="torso",
                     position=np.array([0.5, -0.5, 0.0]))
    skeleton.add_bone("right_knee", parent_name="right_hip",
                     position=np.array([0.0, -1.5, 0.0]))
    skeleton.add_bone("right_foot", parent_name="right_knee",
                     position=np.array([0.0, -1.5, 0.0]))
    
    return skeleton


def create_arm_skeleton() -> Skeleton:
    """Create a simple arm skeleton for testing."""
    skeleton = Skeleton("arm")
    
    skeleton.add_bone("shoulder", position=np.array([0.0, 0.0, 0.0]))
    skeleton.add_bone("elbow", parent_name="shoulder",
                     position=np.array([2.0, 0.0, 0.0]))
    skeleton.add_bone("wrist", parent_name="elbow",
                     position=np.array([2.0, 0.0, 0.0]))
    skeleton.add_bone("hand", parent_name="wrist",
                     position=np.array([1.0, 0.0, 0.0]))
    
    return skeleton
