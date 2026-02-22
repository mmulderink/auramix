"""
Procedural Animation System
Core system for generating 3D animations and projecting to 2D frame streams.
Maintains model state and processes transformations in real-time.
"""

import numpy as np
from typing import Dict, List, Tuple, Generator, Optional, Any, Union
from dataclasses import dataclass, field
import time
import math

try:
    from .model import Model3D, RiggedModel
    from .behavior_script import TransformCommand, BehaviorScript
    from .rigging import Bone
except ImportError:
    from model import Model3D, RiggedModel
    from behavior_script import TransformCommand, BehaviorScript
    from rigging import Bone


@dataclass
class ModelState:
    """Represents the current state of a 3D model."""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))  # Euler angles (degrees)
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    
    def copy(self) -> 'ModelState':
        """Create a deep copy of the state."""
        return ModelState(
            position=self.position.copy(),
            rotation=self.rotation.copy(),
            scale=self.scale.copy()
        )


@dataclass
class BoneState:
    """Represents the current state of a bone in a rigged model."""
    name: str
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    
    def copy(self) -> 'BoneState':
        """Create a deep copy of the bone state."""
        return BoneState(
            name=self.name,
            position=self.position.copy(),
            rotation=self.rotation.copy(),
            scale=self.scale.copy()
        )


@dataclass
class Frame2D:
    """Represents a 2D projected animation frame."""
    frame_number: int
    timestamp: float
    projected_vertices: np.ndarray  # 2D coordinates
    faces: List[Tuple[int, int, int]]
    state: ModelState
    normals: Optional[np.ndarray] = None  # Face normals for shading
    face_colors: Optional[List[Tuple[float, float, float]]] = None  # RGB colors per face
    transformed_vertices: Optional[np.ndarray] = None  # 3D coordinates for depth sorting
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransformationEngine:
    """Handles all 3D transformations."""
    
    @staticmethod
    def translation_matrix(x: float, y: float, z: float) -> np.ndarray:
        """Create a 4x4 translation matrix."""
        return np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotation_matrix_x(angle_deg: float) -> np.ndarray:
        """Create a 4x4 rotation matrix around X axis."""
        angle = np.radians(angle_deg)
        c, s = np.cos(angle), np.sin(angle)
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotation_matrix_y(angle_deg: float) -> np.ndarray:
        """Create a 4x4 rotation matrix around Y axis."""
        angle = np.radians(angle_deg)
        c, s = np.cos(angle), np.sin(angle)
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotation_matrix_z(angle_deg: float) -> np.ndarray:
        """Create a 4x4 rotation matrix around Z axis."""
        angle = np.radians(angle_deg)
        c, s = np.cos(angle), np.sin(angle)
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def scale_matrix(x: float, y: float, z: float) -> np.ndarray:
        """Create a 4x4 scale matrix."""
        return np.array([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def get_transform_matrix(state: ModelState) -> np.ndarray:
        """Get the complete transformation matrix for a given state."""
        # Order: Scale -> Rotate -> Translate
        T = TransformationEngine.translation_matrix(*state.position)
        Rx = TransformationEngine.rotation_matrix_x(state.rotation[0])
        Ry = TransformationEngine.rotation_matrix_y(state.rotation[1])
        Rz = TransformationEngine.rotation_matrix_z(state.rotation[2])
        S = TransformationEngine.scale_matrix(*state.scale)
        
        # Combine transforms: T * Rz * Ry * Rx * S
        return T @ Rz @ Ry @ Rx @ S
    
    @staticmethod
    def apply_transform(vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """Apply transformation matrix to vertices."""
        # Convert to homogeneous coordinates
        ones = np.ones((vertices.shape[0], 1))
        vertices_h = np.hstack([vertices, ones])
        
        # Apply transformation
        transformed = (matrix @ vertices_h.T).T
        
        # Convert back to 3D coordinates
        return transformed[:, :3]
    
    @staticmethod
    def easing_function(t: float, easing: str = 'linear') -> float:
        """Apply easing function to time parameter t (0-1)."""
        t = np.clip(t, 0, 1)
        
        if easing == 'linear':
            return t
        elif easing == 'ease_in':
            return t * t
        elif easing == 'ease_out':
            return t * (2 - t)
        elif easing == 'ease_in_out':
            return t * t * (3 - 2 * t)
        elif easing == 'ease_in_cubic':
            return t * t * t
        elif easing == 'ease_out_cubic':
            return (t - 1) * (t - 1) * (t - 1) + 1
        else:
            return t


class ProjectionEngine:
    """Handles 3D to 2D projection."""
    
    def __init__(self, width: int = 800, height: int = 600, fov: float = 60):
        self.width = width
        self.height = height
        self.fov = fov
        self.aspect_ratio = width / height
        self.camera_distance = 10.0
        
        # Projection matrix
        self.projection_matrix = self._create_projection_matrix()
    
    def _create_projection_matrix(self) -> np.ndarray:
        """Create perspective projection matrix."""
        near, far = 0.1, 100.0
        f = 1.0 / np.tan(np.radians(self.fov) / 2)
        
        return np.array([
            [f / self.aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ], dtype=float)

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self.projection_matrix = self._create_projection_matrix()
    
    def project_vertices(self, vertices_3d: np.ndarray) -> np.ndarray:
        """Project 3D vertices to 2D screen space."""
        # Offset vertices by camera distance
        vertices_camera = vertices_3d.copy()
        vertices_camera[:, 2] -= self.camera_distance
        
        # Convert to homogeneous coordinates
        ones = np.ones((vertices_camera.shape[0], 1))
        vertices_h = np.hstack([vertices_camera, ones])
        
        # Apply projection
        projected = (self.projection_matrix @ vertices_h.T).T
        
        # Perspective divide
        projected[:, :3] /= projected[:, 3:4]
        
        # Convert to screen coordinates
        screen_coords = np.zeros((vertices_3d.shape[0], 2))
        screen_coords[:, 0] = (projected[:, 0] + 1) * self.width / 2
        screen_coords[:, 1] = (1 - projected[:, 1]) * self.height / 2
        
        return screen_coords


class AnimationSystem:
    """
    Main procedural animation system.
    Manages model state, processes transformations, and streams 2D frames.
    Supports both simple models and rigged models with bones.
    """
    
    def __init__(self, model: Union[Model3D, RiggedModel], width: int = 800, height: int = 600, fps: int = 60):
        self.model = model
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_time = 1.0 / fps
        
        # Detect model type
        self.is_rigged = isinstance(model, RiggedModel)
        
        # State management
        self.current_state = ModelState()
        self.base_state = self.current_state.copy()
        self.base_vertices = model.get_vertices_array() if not self.is_rigged else model.bind_vertices.copy()
        
        # Bone states for rigged models
        self.bone_states: Dict[str, BoneState] = {}
        self.bone_start_states: Dict[str, BoneState] = {}
        
        if self.is_rigged:
            # Initialize bone states
            for bone_name in model.skeleton.get_bone_names():
                self.bone_states[bone_name] = BoneState(name=bone_name)
        
        # Engines
        self.transform_engine = TransformationEngine()
        self.projection_engine = ProjectionEngine(width, height)
        
        # Frame tracking
        self.frame_number = 0
        self.total_time = 0.0
        
        # Animation state
        self.is_playing = False
        self.current_command: Optional[TransformCommand] = None
        self.command_start_time = 0.0
        self.command_start_state: Optional[ModelState] = None
    
    def reset(self):
        """Reset animation system to initial state (preserves current model state)."""
        # Note: We DON'T reset current_state here - it should persist
        # Only reset playback-related fields
        
        # Reset bone states for rigged models
        if self.is_rigged:
            for bone_name in self.bone_states:
                self.bone_states[bone_name] = BoneState(name=bone_name)
            self.model.reset_pose()
        
        self.frame_number = 0
        self.total_time = 0.0
        self.is_playing = False
        self.current_command = None

    def set_base_state(self):
        """Capture the current state as the base/idle state."""
        self.base_state = self.current_state.copy()

    def reset_state(self):
        """Reset model state back to the captured base state."""
        self.current_state = self.base_state.copy()

        if self.is_rigged:
            for bone_name in self.bone_states:
                self.bone_states[bone_name] = BoneState(name=bone_name)
            self.model.reset_pose()
    
    def apply_transform_command(self, command: TransformCommand, progress: float = 1.0):
        """Apply a transformation command with given progress (0-1)."""
        # Apply easing
        eased_progress = self.transform_engine.easing_function(progress, command.easing)
        
        # Check if this targets a specific bone
        if command.target_bone and self.is_rigged:
            self._apply_bone_transform(command, eased_progress)
        else:
            self._apply_model_transform(command, eased_progress)
    
    def _apply_model_transform(self, command: TransformCommand, progress: float):
        """Apply transformation to the whole model."""
        if command.transform_type == 'translate':
            delta = np.array([
                command.params.get('x', 0),
                command.params.get('y', 0),
                command.params.get('z', 0)
            ]) * progress
            
            if self.command_start_state:
                self.current_state.position = self.command_start_state.position + delta
            else:
                self.current_state.position += delta
        
        elif command.transform_type == 'rotate':
            delta = np.array([
                command.params.get('x', 0),
                command.params.get('y', 0),
                command.params.get('z', 0)
            ]) * progress
            
            if self.command_start_state:
                self.current_state.rotation = self.command_start_state.rotation + delta
            else:
                self.current_state.rotation += delta
        
        elif command.transform_type == 'scale':
            target = np.array([
                command.params.get('x', 1),
                command.params.get('y', 1),
                command.params.get('z', 1)
            ])
            
            if self.command_start_state:
                start = self.command_start_state.scale
                self.current_state.scale = start + (target - start) * progress
            else:
                self.current_state.scale = target * progress
        
        elif command.transform_type == 'composed':
            # Apply multiple transforms in sequence
            for transform in command.params.get('transforms', []):
                sub_cmd = TransformCommand(
                    transform_type=transform['type'],
                    params=transform,
                    duration=0.0
                )
                self._apply_model_transform(sub_cmd, progress)
    
    def _apply_bone_transform(self, command: TransformCommand, progress: float):
        """Apply transformation to a specific bone."""
        bone_name = command.target_bone
        
        if bone_name not in self.bone_states:
            print(f"Warning: Bone '{bone_name}' not found")
            return
        
        bone_state = self.bone_states[bone_name]
        bone = self.model.get_bone(bone_name)
        
        if not bone:
            return
        
        # Get start state for this bone
        start_state = self.bone_start_states.get(bone_name)
        if not start_state:
            start_state = BoneState(
                name=bone_name,
                position=bone.local_position.copy(),
                rotation=bone.local_rotation.copy(),
                scale=bone.local_scale.copy()
            )
        
        if command.transform_type == 'translate':
            delta = np.array([
                command.params.get('x', 0),
                command.params.get('y', 0),
                command.params.get('z', 0)
            ]) * progress
            
            new_position = start_state.position + delta
            bone_state.position = new_position
            bone.set_position(new_position)
        
        elif command.transform_type == 'rotate':
            delta = np.array([
                command.params.get('x', 0),
                command.params.get('y', 0),
                command.params.get('z', 0)
            ]) * progress
            
            new_rotation = start_state.rotation + delta
            bone_state.rotation = new_rotation
            bone.set_rotation(new_rotation)
        
        elif command.transform_type == 'scale':
            target = np.array([
                command.params.get('x', 1),
                command.params.get('y', 1),
                command.params.get('z', 1)
            ])
            
            new_scale = start_state.scale + (target - start_state.scale) * progress
            bone_state.scale = new_scale
            bone.set_scale(new_scale)
        
        elif command.transform_type == 'composed':
            for transform in command.params.get('transforms', []):
                sub_cmd = TransformCommand(
                    transform_type=transform['type'],
                    params=transform,
                    duration=0.0,
                    target_bone=bone_name
                )
                self._apply_bone_transform(sub_cmd, progress)
        
        # Mark model as dirty
        self.model.mark_dirty()
    
    def process_command(self, command: TransformCommand, dt: float) -> bool:
        """
        Process a command for one time step.
        Returns True if command is complete, False if still in progress.
        """
        if self.current_command != command:
            # New command
            self.current_command = command
            self.command_start_time = self.total_time
            self.command_start_state = self.current_state.copy()
            
            # Save bone start states for rigged models
            if self.is_rigged and command.target_bone:
                bone_name = command.target_bone
                if bone_name in self.bone_states:
                    bone = self.model.get_bone(bone_name)
                    if bone:
                        self.bone_start_states[bone_name] = BoneState(
                            name=bone_name,
                            position=bone.local_position.copy(),
                            rotation=bone.local_rotation.copy(),
                            scale=bone.local_scale.copy()
                        )
        
        if command.duration <= 0:
            # Instant transform
            self.apply_transform_command(command, 1.0)
            return True
        else:
            # Animated transform
            elapsed = self.total_time - self.command_start_time
            progress = min(elapsed / command.duration, 1.0)
            
            self.apply_transform_command(command, progress)
            
            return progress >= 1.0
    
    def generate_frame(self) -> Frame2D:
        """Generate current 2D frame from current state."""
        if self.is_rigged:
            # For rigged models, get transformed vertices from skeleton
            transformed_vertices = self.model.get_transformed_vertices()

            # Apply global model state to rigged output (e.g., initial orientation)
            if transformed_vertices.size > 0:
                transform_matrix = self.transform_engine.get_transform_matrix(self.current_state)
                transformed_vertices = self.transform_engine.apply_transform(
                    transformed_vertices, transform_matrix
                )
        else:
            # For simple models, apply global transformation
            transform_matrix = self.transform_engine.get_transform_matrix(self.current_state)
            transformed_vertices = self.transform_engine.apply_transform(
                self.base_vertices, transform_matrix
            )
        
        # Project to 2D
        projected = self.projection_engine.project_vertices(transformed_vertices)
        
        # Calculate face normals for shading
        normals = self._calculate_face_normals(transformed_vertices)
        
        # Get face colors if model supports them
        face_colors = None
        if hasattr(self.model, 'get_face_colors'):
            face_colors = self.model.get_face_colors()
        
        # Create frame
        frame = Frame2D(
            frame_number=self.frame_number,
            timestamp=self.total_time,
            projected_vertices=projected,
            faces=self.model.get_faces(),
            state=self.current_state.copy(),
            normals=normals,
            face_colors=face_colors,
            transformed_vertices=transformed_vertices,
            metadata={
                'width': self.width,
                'height': self.height,
                'fps': self.fps
            }
        )
        
        return frame
    
    def stream_frames(self, script: BehaviorScript, max_frames: Optional[int] = None) -> Generator[Frame2D, None, None]:
        """
        Stream animation frames based on behavior script.
        Yields Frame2D objects in real-time.
        """
        self.reset()
        script.reset()

        effect_type = getattr(script, "effect_type", None)
        effect_duration = float(getattr(script, "effect_duration", 0.0)) if effect_type else 0.0
        effect_id = f"{script.name}:{id(script)}" if effect_type else None
        effect_start_time = self.total_time
        
        frame_count = 0
        
        while script.has_more_commands() or self.current_command:
            # Get next command if needed
            if not self.current_command:
                self.current_command = script.get_next_command()
                if not self.current_command:
                    break
                self.command_start_time = self.total_time
                self.command_start_state = self.current_state.copy()
            
            # Process current command
            is_complete = self.process_command(self.current_command, self.frame_time)
            
            # Generate frame
            frame = self.generate_frame()
            if effect_type:
                effect_elapsed = self.total_time - effect_start_time
                frame.metadata.update({
                    "effect_type": effect_type,
                    "effect_id": effect_id,
                    "effect_duration": effect_duration,
                    "effect_elapsed": effect_elapsed
                })
            yield frame
            
            # Update timing
            self.frame_number += 1
            self.total_time += self.frame_time
            frame_count += 1
            
            # Clear completed command
            if is_complete:
                self.current_command = None
            
            # Check max frames
            if max_frames and frame_count >= max_frames:
                break
    
    def get_current_frame(self) -> Frame2D:
        """Get the current frame without advancing time."""
        return self.generate_frame()
    
    def update(self, dt: float):
        """Update animation by time delta."""
        self.total_time += dt
        self.frame_number += 1
    
    def set_state(self, position: Optional[np.ndarray] = None,
                 rotation: Optional[np.ndarray] = None,
                 scale: Optional[np.ndarray] = None):
        """Manually set the model state."""
        if position is not None:
            self.current_state.position = position
        if rotation is not None:
            self.current_state.rotation = rotation
        if scale is not None:
            self.current_state.scale = scale

    def set_render_size(self, width: int, height: int):
        self.width = width
        self.height = height
        self.projection_engine.resize(width, height)
    
    def get_state(self) -> ModelState:
        """Get current model state."""
        return self.current_state.copy()
    
    def _calculate_face_normals(self, vertices: np.ndarray) -> np.ndarray:
        """
        Calculate normal vectors for each face.
        Returns array of shape (num_faces, 3) with normalized normal vectors.
        """
        faces = self.model.get_faces()
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
