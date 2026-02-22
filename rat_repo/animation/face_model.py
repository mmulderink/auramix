"""
Custom Face Models
Creates 3D face geometry with beard and sunglasses.
"""

import numpy as np
from typing import List, Tuple
try:
    from .model import Model3D
except ImportError:
    from model import Model3D


class FaceModel(Model3D):
    """
    A 3D face model with beard and sunglasses.
    """
    
    def __init__(self, name: str = "face"):
        self.name = name
        self.vertices: List[Tuple[float, float, float]] = []
        self.faces: List[Tuple[int, int, int]] = []
        self.face_colors: List[Tuple[float, float, float]] = []  # RGB values (0-1)
        
        # Build the face components
        self._build_face()
    
    def _build_face(self):
        """Build a face with beard and sunglasses."""
        vertices = []
        faces = []
        colors = []
        
        # Color definitions (RGB, 0-1 range)
        peach = (1.0, 0.8, 0.6)      # Face color
        brown = (0.4, 0.26, 0.13)    # Beard color
        grey = (0.2, 0.2, 0.2)       # Sunglasses color
        
        # HEAD (larger sphere-like shape)
        head_verts, head_faces = self._create_head()
        vertices.extend(head_verts)
        faces.extend(head_faces)
        colors.extend([peach] * len(head_faces))  # All head faces are peach
        
        # BEARD (lower part of face)
        beard_offset = len(vertices)
        beard_verts, beard_faces = self._create_beard()
        vertices.extend(beard_verts)
        faces.extend([(f[0] + beard_offset, f[1] + beard_offset, f[2] + beard_offset) 
                      for f in beard_faces])
        colors.extend([brown] * len(beard_faces))  # All beard faces are brown
        
        # SUNGLASSES (two rectangular lenses with bridge)
        glasses_offset = len(vertices)
        glasses_verts, glasses_faces = self._create_sunglasses()
        vertices.extend(glasses_verts)
        faces.extend([(f[0] + glasses_offset, f[1] + glasses_offset, f[2] + glasses_offset) 
                      for f in glasses_faces])
        colors.extend([grey] * len(glasses_faces))  # All sunglasses faces are grey
        
        self.vertices = vertices
        self.faces = faces
        self.face_colors = colors
    
    def _create_head(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Create head geometry (rounded cube approximation)."""
        vertices = []
        faces = []
        
        # Head base (larger cube)
        size = 2.0
        vertices = [
            (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size),  # Back
            (-size, -size, size), (size, -size, size), (size, size, size), (-size, size, size)       # Front (face)
        ]
        
        faces = [
            # Back
            (0, 1, 2), (0, 2, 3),
            # Front (face side)
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
        
        return vertices, faces
    
    def _create_beard(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Create beard geometry (bushy multi-segment beard)."""
        vertices = []
        faces = []
        
        # Bushier beard with multiple segments
        # Beard hangs down from chin (negative Y = below center, appears at bottom of screen)
        z_base = 2.2  # Forward from face
        
        # SECTION 1: Upper beard (attached to chin)
        w1 = 1.6
        vertices.extend([
            # Top ring (attached to face at chin level)
            (-w1, -1.0, z_base - 0.1),     # 0
            (-w1*0.7, -1.0, z_base + 0.3), # 1
            (0, -1.0, z_base + 0.5),       # 2
            (w1*0.7, -1.0, z_base + 0.3),  # 3
            (w1, -1.0, z_base - 0.1),      # 4
            # Bottom ring (wider and extends down)
            (-w1*1.1, -1.8, z_base + 0.1), # 5
            (-w1*0.9, -1.8, z_base + 0.6), # 6
            (0, -1.8, z_base + 0.8),       # 7
            (w1*0.9, -1.8, z_base + 0.6),  # 8
            (w1*1.1, -1.8, z_base + 0.1),  # 9
        ])
        
        # SECTION 2: Middle beard (fuller)
        base = 10
        vertices.extend([
            # Extends further down
            (-w1*1.2, -2.5, z_base + 0.2), # 10
            (-w1*1.0, -2.5, z_base + 0.7), # 11
            (-w1*0.3, -2.5, z_base + 1.0), # 12
            (w1*0.3, -2.5, z_base + 1.0),  # 13
            (w1*1.0, -2.5, z_base + 0.7),  # 14
            (w1*1.2, -2.5, z_base + 0.2),  # 15
        ])
        
        # SECTION 3: Lower beard (bushiest, tapers slightly)
        base = 16
        vertices.extend([
            (-w1*1.1, -3.2, z_base + 0.3), # 16
            (-w1*0.8, -3.2, z_base + 0.8), # 17
            (0, -3.2, z_base + 0.9),       # 18
            (w1*0.8, -3.2, z_base + 0.8),  # 19
            (w1*1.1, -3.2, z_base + 0.3),  # 20
        ])
        
        # SECTION 4: Beard tip (rounded bottom)
        base = 21
        vertices.extend([
            (-w1*0.6, -3.7, z_base + 0.4), # 21
            (0, -3.7, z_base + 0.6),       # 22
            (w1*0.6, -3.7, z_base + 0.4),  # 23
        ])
        
        # Create faces connecting the sections
        # Section 1 - top to middle
        faces.extend([
            # Left side
            (0, 5, 1), (1, 5, 6),
            (1, 6, 2), (2, 6, 7),
            # Right side
            (2, 7, 3), (3, 7, 8),
            (3, 8, 4), (4, 8, 9),
            # Back
            (0, 4, 5), (4, 9, 5),
        ])
        
        # Section 2 - middle to lower-middle
        faces.extend([
            # Left outer
            (5, 10, 6), (6, 10, 11),
            # Left inner
            (6, 11, 7), (7, 11, 12),
            # Center
            (7, 12, 8), (8, 12, 13),
            # Right inner
            (8, 13, 9), (9, 13, 14),
            # Right outer
            (9, 14, 10), (10, 14, 15),
            # Wrap back
            (5, 9, 10), (9, 15, 10),
        ])
        
        # Section 3 - lower-middle to lower
        faces.extend([
            # Left
            (10, 16, 11), (11, 16, 17),
            (11, 17, 12), (12, 17, 18),
            # Right
            (12, 18, 13), (13, 18, 19),
            (13, 19, 14), (14, 19, 20),
            # Back
            (10, 15, 16), (15, 20, 16),
        ])
        
        # Section 4 - lower to tip
        faces.extend([
            # Left
            (16, 21, 17), (17, 21, 22),
            (17, 22, 18), (18, 22, 19),
            # Right
            (19, 22, 20), (20, 22, 23),
            (20, 23, 16), (16, 23, 21),
            # Bottom cap
            (21, 23, 22),
        ])
        
        return vertices, faces
    
    def _create_sunglasses(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Create sunglasses geometry (two lenses with bridge)."""
        vertices = []
        faces = []
        
        # Sunglasses positioned on upper part of face (positive Y = top)
        lens_w, lens_h, lens_d = 0.8, 0.6, 0.2
        y_pos = 0.5  # Upper part of face
        z_pos = 2.3  # In front of face
        gap = 0.3    # Gap between lenses
        
        # LEFT LENS
        left_x = -gap / 2 - lens_w
        vertices.extend([
            # Back face
            (left_x, y_pos - lens_h/2, z_pos),
            (left_x + lens_w, y_pos - lens_h/2, z_pos),
            (left_x + lens_w, y_pos + lens_h/2, z_pos),
            (left_x, y_pos + lens_h/2, z_pos),
            # Front face
            (left_x, y_pos - lens_h/2, z_pos + lens_d),
            (left_x + lens_w, y_pos - lens_h/2, z_pos + lens_d),
            (left_x + lens_w, y_pos + lens_h/2, z_pos + lens_d),
            (left_x, y_pos + lens_h/2, z_pos + lens_d)
        ])
        
        base = 0
        faces.extend([
            (base+0, base+1, base+2), (base+0, base+2, base+3),
            (base+4, base+5, base+6), (base+4, base+6, base+7),
            (base+0, base+3, base+7), (base+0, base+7, base+4),
            (base+1, base+5, base+6), (base+1, base+6, base+2),
            (base+0, base+1, base+5), (base+0, base+5, base+4),
            (base+3, base+2, base+6), (base+3, base+6, base+7)
        ])
        
        # RIGHT LENS
        right_x = gap / 2
        base = len(vertices)
        vertices.extend([
            # Back face
            (right_x, y_pos - lens_h/2, z_pos),
            (right_x + lens_w, y_pos - lens_h/2, z_pos),
            (right_x + lens_w, y_pos + lens_h/2, z_pos),
            (right_x, y_pos + lens_h/2, z_pos),
            # Front face
            (right_x, y_pos - lens_h/2, z_pos + lens_d),
            (right_x + lens_w, y_pos - lens_h/2, z_pos + lens_d),
            (right_x + lens_w, y_pos + lens_h/2, z_pos + lens_d),
            (right_x, y_pos + lens_h/2, z_pos + lens_d)
        ])
        
        faces.extend([
            (base+0, base+1, base+2), (base+0, base+2, base+3),
            (base+4, base+5, base+6), (base+4, base+6, base+7),
            (base+0, base+3, base+7), (base+0, base+7, base+4),
            (base+1, base+5, base+6), (base+1, base+6, base+2),
            (base+0, base+1, base+5), (base+0, base+5, base+4),
            (base+3, base+2, base+6), (base+3, base+6, base+7)
        ])
        
        # BRIDGE (connects the lenses)
        bridge_w = gap
        bridge_h = 0.15
        bridge_d = 0.15
        base = len(vertices)
        vertices.extend([
            # Simple bridge box
            (-bridge_w/2, y_pos - bridge_h/2, z_pos),
            (bridge_w/2, y_pos - bridge_h/2, z_pos),
            (bridge_w/2, y_pos + bridge_h/2, z_pos),
            (-bridge_w/2, y_pos + bridge_h/2, z_pos),
            (-bridge_w/2, y_pos - bridge_h/2, z_pos + bridge_d),
            (bridge_w/2, y_pos - bridge_h/2, z_pos + bridge_d),
            (bridge_w/2, y_pos + bridge_h/2, z_pos + bridge_d),
            (-bridge_w/2, y_pos + bridge_h/2, z_pos + bridge_d)
        ])
        
        faces.extend([
            (base+0, base+1, base+2), (base+0, base+2, base+3),
            (base+4, base+5, base+6), (base+4, base+6, base+7),
            (base+0, base+3, base+7), (base+0, base+7, base+4),
            (base+1, base+5, base+6), (base+1, base+6, base+2),
            (base+0, base+1, base+5), (base+0, base+5, base+4),
            (base+3, base+2, base+6), (base+3, base+6, base+7)
        ])
        
        return vertices, faces
    
    def get_face_colors(self) -> List[Tuple[float, float, float]]:
        """Return face colors as list of RGB tuples (0-1 range)."""
        return self.face_colors


def calculate_face_normals(vertices: np.ndarray, faces: List[Tuple[int, int, int]]) -> np.ndarray:
    """
    Calculate normal vectors for each face.
    Returns array of shape (num_faces, 3) with normalized normal vectors.
    """
    normals = []
    
    for face in faces:
        # Get three vertices of the triangle
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]
        
        # Calculate two edge vectors
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Calculate normal via cross product
        normal = np.cross(edge1, edge2)
        
        # Normalize
        length = np.linalg.norm(normal)
        if length > 0:
            normal = normal / length
        else:
            normal = np.array([0, 0, 1])  # Default normal
        
        normals.append(normal)
    
    return np.array(normals)


def calculate_shading_intensity(normals: np.ndarray, 
                                light_direction: np.ndarray = np.array([0, 0, 1])) -> np.ndarray:
    """
    Calculate shading intensity for each face based on normal direction.
    Uses simple directional lighting.
    
    Args:
        normals: Face normal vectors
        light_direction: Direction of light (default: facing camera)
    
    Returns:
        Array of intensities (0-1) for each face
    """
    # Normalize light direction
    light_dir = light_direction / np.linalg.norm(light_direction)
    
    # Calculate dot product (cosine of angle between normal and light)
    intensities = np.dot(normals, light_dir)
    
    # Clamp to 0-1 range (negative means facing away from light)
    intensities = np.clip(intensities, 0.0, 1.0)
    
    # Add ambient lighting (so nothing is completely black)
    ambient = 0.3
    intensities = ambient + (1.0 - ambient) * intensities
    
    return intensities
