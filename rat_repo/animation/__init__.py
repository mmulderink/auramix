"""
Procedural 3D Animation System

A real-time 3D animation generation system with skeletal rigging,
state management, hardware-accelerated rendering, and transformation sequencing.
"""

from .animation_system import AnimationSystem, Frame2D, ModelState
from .behavior_script import BehaviorScript, TransformCommand
from .model import Model3D, RiggedModel
from .rigging import Skeleton, Bone
from .renderer_gl import GLAnimationPlayer

__version__ = "1.0.0"

__all__ = [
    "AnimationSystem",
    "Frame2D",
    "ModelState",
    "BehaviorScript",
    "TransformCommand",
    "Model3D",
    "RiggedModel",
    "Skeleton",
    "Bone",
    "GLAnimationPlayer",
]
