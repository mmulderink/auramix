"""
3D Model Definition
Placeholder for defining 3D model shapes/figures.
This will be expanded later with actual geometry.
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
try:
    from .rigging import Skeleton, Bone
except ImportError:
    from rigging import Skeleton, Bone


class Model3D:
    """
    Placeholder class for 3D models.
    Will be expanded with actual geometry, vertices, faces, etc.
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.vertices: List[Tuple[float, float, float]] = []
        self.faces: List[Tuple[int, int, int]] = []
        
        # Initialize with a simple cube placeholder
        self._initialize_cube()
    
    def _initialize_cube(self):
        """Initialize a simple cube as placeholder geometry."""
        # Cube vertices (8 corners)
        self.vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Back face
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)       # Front face
        ]
        
        # Cube faces (12 triangles, 2 per side)
        self.faces = [
            # Back
            (0, 1, 2), (0, 2, 3),
            # Front
            (4, 5, 6), (4, 6, 7),
            # Left
            (0, 3, 7), (0, 7, 4),
            # Right
            (1, 5, 6), (1, 6, 2),
            # Bottom
            (0, 1, 5), (0, 5, 4),
            # Top
            (3, 2, 6), (3, 6, 7)
        ]
    
    def get_vertices_array(self) -> np.ndarray:
        """Return vertices as numpy array for transformation."""
        return np.array(self.vertices, dtype=float)
    
    def get_faces(self) -> List[Tuple[int, int, int]]:
        """Return face indices."""
        return self.faces
    
    def vertex_count(self) -> int:
        """Return number of vertices."""
        return len(self.vertices)


# Additional model types can be added here later
class Sphere(Model3D):
    """Placeholder for sphere geometry."""
    pass


class Cylinder(Model3D):
    """Placeholder for cylinder geometry."""
    pass


class CustomModel(Model3D):
    """Placeholder for custom model loading."""
    pass


class RiggedModel:
    """
    A 3D model with skeletal rigging for articulated animation.
    Supports hierarchical bone transformations and vertex skinning.
    """
    
    def __init__(self, name: str = "rigged_model", skeleton: Optional[Skeleton] = None):
        self.name = name
        self.skeleton = skeleton if skeleton else Skeleton(name + "_skeleton")
        
        # Base mesh data (bind pose)
        self.bind_vertices: np.ndarray = np.array([])
        self.faces: List[Tuple[int, int, int]] = []
        
        # Skinning weights (which vertices are affected by which bones)
        self.skin_weights: Dict[str, Dict[int, float]] = {}  # bone_name -> {vertex_idx: weight}
        
        # Cached transformed vertices
        self._transformed_vertices: Optional[np.ndarray] = None
        self._dirty = True
    
    def set_mesh(self, vertices: np.ndarray, faces: List[Tuple[int, int, int]]):
        """Set the mesh geometry (bind pose)."""
        self.bind_vertices = vertices.copy()
        self.faces = faces
        self._dirty = True
    
    def set_cube_mesh(self):
        """Set a simple cube as the mesh."""
        vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face
        ], dtype=float)
        
        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]
        
        self.set_mesh(vertices, faces)
    
    def attach_vertices_to_bone(self, bone_name: str, vertex_indices: List[int], 
                               weights: Optional[List[float]] = None):
        """
        Attach specific vertices to a bone with optional weights.
        Vertices can be influenced by multiple bones.
        """
        if bone_name not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone_name}' not found in skeleton")
        
        if bone_name not in self.skin_weights:
            self.skin_weights[bone_name] = {}
        
        if weights is None:
            weights = [1.0] * len(vertex_indices)
        
        for idx, weight in zip(vertex_indices, weights):
            self.skin_weights[bone_name][idx] = weight
        
        # Also update the bone's vertex info
        bone = self.skeleton.get_bone(bone_name)
        bone.attach_vertices(vertex_indices, weights)
        
        self._dirty = True
    
    def auto_weight_vertices(self):
        """
        Automatically assign vertices to nearest bones.
        Simple distance-based weighting.
        """
        if len(self.bind_vertices) == 0:
            return
        
        for bone_name, bone in self.skeleton.bones.items():
            # Get bone position in world space
            bone_world_matrix = bone.get_world_matrix()
            bone_pos = bone_world_matrix[:3, 3]
            
            # Find vertices close to this bone
            vertex_indices = []
            weights = []
            
            for i, vertex in enumerate(self.bind_vertices):
                distance = np.linalg.norm(vertex - bone_pos)
                
                # Weight based on inverse distance (closer = more influence)
                if distance < 3.0:  # Only consider nearby vertices
                    weight = 1.0 / (1.0 + distance)
                    vertex_indices.append(i)
                    weights.append(weight)
            
            if vertex_indices:
                self.attach_vertices_to_bone(bone_name, vertex_indices, weights)
        
        # Normalize weights so each vertex's total weight = 1.0
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize skin weights so each vertex's total weight = 1.0."""
        vertex_total_weights = {}
        
        # Calculate total weight per vertex
        for bone_name, bone_weights in self.skin_weights.items():
            for vertex_idx, weight in bone_weights.items():
                if vertex_idx not in vertex_total_weights:
                    vertex_total_weights[vertex_idx] = 0.0
                vertex_total_weights[vertex_idx] += weight
        
        # Normalize
        for bone_name in self.skin_weights:
            for vertex_idx in self.skin_weights[bone_name]:
                total = vertex_total_weights.get(vertex_idx, 1.0)
                if total > 0:
                    self.skin_weights[bone_name][vertex_idx] /= total
    
    def get_transformed_vertices(self, force_recalc: bool = False) -> np.ndarray:
        """
        Get vertices transformed by the current skeleton pose.
        Uses skinning to blend bone transformations.
        """
        if not self._dirty and self._transformed_vertices is not None and not force_recalc:
            return self._transformed_vertices
        
        if len(self.bind_vertices) == 0:
            return np.array([])
        
        # Initialize with zeros
        transformed = np.zeros_like(self.bind_vertices)
        
        # Apply skinning: blend transformations from all influencing bones
        for bone_name, bone_weights in self.skin_weights.items():
            bone = self.skeleton.get_bone(bone_name)
            if bone is None:
                continue
            
            # Get bone's world transformation
            bone_matrix = bone.get_world_matrix()
            
            # Transform vertices influenced by this bone
            for vertex_idx, weight in bone_weights.items():
                if vertex_idx >= len(self.bind_vertices):
                    continue
                
                # Transform vertex
                vertex = self.bind_vertices[vertex_idx]
                vertex_h = np.append(vertex, 1.0)  # Homogeneous coordinates
                transformed_vertex = (bone_matrix @ vertex_h)[:3]
                
                # Blend with weight
                transformed[vertex_idx] += transformed_vertex * weight
        
        self._transformed_vertices = transformed
        self._dirty = False
        return self._transformed_vertices
    
    def get_vertices_array(self) -> np.ndarray:
        """Return transformed vertices."""
        return self.get_transformed_vertices()
    
    def get_faces(self) -> List[Tuple[int, int, int]]:
        """Return face indices."""
        return self.faces
    
    def vertex_count(self) -> int:
        """Return number of vertices."""
        return len(self.bind_vertices)
    
    def mark_dirty(self):
        """Mark the model as needing recalculation."""
        self._dirty = True
    
    def reset_pose(self):
        """Reset skeleton to bind pose."""
        self.skeleton.reset_pose()
        self.mark_dirty()
    
    def get_bone(self, name: str) -> Optional[Bone]:
        """Get bone by name."""
        return self.skeleton.get_bone(name)
    
    def __repr__(self):
        return (f"RiggedModel('{self.name}', vertices={len(self.bind_vertices)}, "
                f"bones={len(self.skeleton.bones)})")


def create_simple_rigged_cube() -> RiggedModel:
    """Create a simple rigged cube with a basic skeleton."""
    from rigging import create_arm_skeleton
    
    # Create model with arm skeleton
    skeleton = create_arm_skeleton()
    model = RiggedModel("rigged_cube", skeleton)
    
    # Set cube mesh
    model.set_cube_mesh()
    
    # Manually assign vertices to bones for demonstration
    # Assign all vertices to shoulder for now (will auto-weight in more complex setups)
    all_indices = list(range(8))
    model.attach_vertices_to_bone("shoulder", all_indices)
    
    return model


def create_articulated_model() -> RiggedModel:
    """Create an articulated model with multiple parts."""
    from rigging import create_simple_skeleton
    
    skeleton = create_simple_skeleton()
    model = RiggedModel("articulated_body", skeleton)
    
    # Create a simple mesh (can be expanded later)
    # For now, use multiple cubes for different body parts
    vertices = []
    faces = []
    
    # Torso cube (larger)
    torso_verts = [
        [-1, 0, -1], [1, 0, -1], [1, 2, -1], [-1, 2, -1],
        [-1, 0, 1], [1, 0, 1], [1, 2, 1], [-1, 2, 1]
    ]
    vertices.extend(torso_verts)
    base_idx = 0
    faces.extend([
        (base_idx+0, base_idx+1, base_idx+2), (base_idx+0, base_idx+2, base_idx+3),
        (base_idx+4, base_idx+5, base_idx+6), (base_idx+4, base_idx+6, base_idx+7),
        (base_idx+0, base_idx+3, base_idx+7), (base_idx+0, base_idx+7, base_idx+4),
        (base_idx+1, base_idx+5, base_idx+6), (base_idx+1, base_idx+6, base_idx+2),
        (base_idx+0, base_idx+1, base_idx+5), (base_idx+0, base_idx+5, base_idx+4),
        (base_idx+3, base_idx+2, base_idx+6), (base_idx+3, base_idx+6, base_idx+7)
    ])
    
    # Head cube (smaller, offset up)
    head_verts = [
        [-0.5, 2, -0.5], [0.5, 2, -0.5], [0.5, 3, -0.5], [-0.5, 3, -0.5],
        [-0.5, 2, 0.5], [0.5, 2, 0.5], [0.5, 3, 0.5], [-0.5, 3, 0.5]
    ]
    base_idx = len(vertices)
    vertices.extend(head_verts)
    faces.extend([
        (base_idx+0, base_idx+1, base_idx+2), (base_idx+0, base_idx+2, base_idx+3),
        (base_idx+4, base_idx+5, base_idx+6), (base_idx+4, base_idx+6, base_idx+7),
        (base_idx+0, base_idx+3, base_idx+7), (base_idx+0, base_idx+7, base_idx+4),
        (base_idx+1, base_idx+5, base_idx+6), (base_idx+1, base_idx+6, base_idx+2),
        (base_idx+0, base_idx+1, base_idx+5), (base_idx+0, base_idx+5, base_idx+4),
        (base_idx+3, base_idx+2, base_idx+6), (base_idx+3, base_idx+6, base_idx+7)
    ])
    
    model.set_mesh(np.array(vertices, dtype=float), faces)
    
    # Attach vertices to bones
    model.attach_vertices_to_bone("torso", list(range(8)))  # First 8 vertices = torso
    model.attach_vertices_to_bone("head", list(range(8, 16)))  # Next 8 = head
    
    return model

