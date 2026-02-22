"""
Rat Head Model
Creates a 3D rat head with ears, snout, whiskers, and eyes.
Includes simple nose rigging for wiggle animations.
"""

import numpy as np
from typing import List, Tuple
try:
    from .model import RiggedModel
    from .rigging import Skeleton
except ImportError:
    from model import RiggedModel
    from rigging import Skeleton


class RatModel(RiggedModel):
    """
    A 3D rat head model with ears, snout, eyes, and whiskers.
    """

    def __init__(self, name: str = "rat"):
        self.name = name
        self.face_colors: List[Tuple[float, float, float]] = []

        skeleton = Skeleton(name + "_skeleton")
        skeleton.add_bone("head", position=np.array([0.0, 0.0, 0.0]))
        skeleton.add_bone("nose", parent_name="head", position=np.array([0.0, -0.5, 3.5]))

        super().__init__(name, skeleton)

        vertices, faces, colors, nose_indices, snout_indices = self._build_rat()
        self.set_mesh(np.array(vertices, dtype=float), faces)
        self.face_colors = colors

        all_indices = list(range(len(vertices)))
        self.attach_vertices_to_bone("head", all_indices)

        nose_weights = [1.0] * len(nose_indices)
        self.attach_vertices_to_bone("nose", nose_indices, nose_weights)

        if snout_indices:
            snout_weights = [0.6] * len(snout_indices)
            self.attach_vertices_to_bone("nose", snout_indices, snout_weights)

        self._normalize_weights()

    def _build_rat(self):
        """Build a rat head with all features."""
        vertices = []
        faces = []
        colors = []

        # Color definitions (RGB, 0-1 range)
        brown = (0.4, 0.26, 0.13)
        light_brown = (0.55, 0.4, 0.25)
        dark_brown = (0.25, 0.15, 0.08)
        pink = (1.0, 0.7, 0.7)
        black = (0.1, 0.1, 0.1)
        white = (0.95, 0.95, 0.9)

        head_verts, head_faces = self._create_head()
        vertices.extend(head_verts)
        faces.extend(head_faces)
        colors.extend([brown] * len(head_faces))

        snout_offset = len(vertices)
        snout_verts, snout_faces = self._create_snout()
        vertices.extend(snout_verts)
        faces.extend([
            (f[0] + snout_offset, f[1] + snout_offset, f[2] + snout_offset)
            for f in snout_faces
        ])
        colors.extend([light_brown] * len(snout_faces))
        snout_indices = list(range(snout_offset, snout_offset + len(snout_verts)))

        nose_offset = len(vertices)
        nose_verts, nose_faces = self._create_nose()
        vertices.extend(nose_verts)
        faces.extend([
            (f[0] + nose_offset, f[1] + nose_offset, f[2] + nose_offset)
            for f in nose_faces
        ])
        colors.extend([pink] * len(nose_faces))
        nose_indices = list(range(nose_offset, nose_offset + len(nose_verts)))

        left_ear_offset = len(vertices)
        left_ear_verts, left_ear_faces = self._create_left_ear()
        vertices.extend(left_ear_verts)
        faces.extend([
            (f[0] + left_ear_offset, f[1] + left_ear_offset, f[2] + left_ear_offset)
            for f in left_ear_faces
        ])
        colors.extend([dark_brown] * len(left_ear_faces))

        right_ear_offset = len(vertices)
        right_ear_verts, right_ear_faces = self._create_right_ear()
        vertices.extend(right_ear_verts)
        faces.extend([
            (f[0] + right_ear_offset, f[1] + right_ear_offset, f[2] + right_ear_offset)
            for f in right_ear_faces
        ])
        colors.extend([dark_brown] * len(right_ear_faces))

        left_eye_offset = len(vertices)
        left_eye_verts, left_eye_faces = self._create_left_eye()
        vertices.extend(left_eye_verts)
        faces.extend([
            (f[0] + left_eye_offset, f[1] + left_eye_offset, f[2] + left_eye_offset)
            for f in left_eye_faces
        ])
        colors.extend([black] * len(left_eye_faces))

        right_eye_offset = len(vertices)
        right_eye_verts, right_eye_faces = self._create_right_eye()
        vertices.extend(right_eye_verts)
        faces.extend([
            (f[0] + right_eye_offset, f[1] + right_eye_offset, f[2] + right_eye_offset)
            for f in right_eye_faces
        ])
        colors.extend([black] * len(right_eye_faces))

        whiskers_offset = len(vertices)
        whiskers_verts, whiskers_faces = self._create_whiskers()
        vertices.extend(whiskers_verts)
        faces.extend([
            (f[0] + whiskers_offset, f[1] + whiskers_offset, f[2] + whiskers_offset)
            for f in whiskers_faces
        ])
        colors.extend([white] * len(whiskers_faces))

        return vertices, faces, colors, nose_indices, snout_indices

    def _create_head(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        w, h, d = 2.2, 1.8, 2.0

        vertices = [
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_snout(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        y_pos = -0.5
        z_start = 2.0
        z_end = 3.5

        w_base = 1.2
        h_base = 0.8
        w_tip = 0.7
        h_tip = 0.5

        vertices = [
            (-w_base, y_pos - h_base / 2, z_start),
            (w_base, y_pos - h_base / 2, z_start),
            (w_base, y_pos + h_base / 2, z_start),
            (-w_base, y_pos + h_base / 2, z_start),
            (-w_tip, y_pos - h_tip / 2, z_end),
            (w_tip, y_pos - h_tip / 2, z_end),
            (w_tip, y_pos + h_tip / 2, z_end),
            (-w_tip, y_pos + h_tip / 2, z_end)
        ]

        faces = [
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (4, 5, 6), (4, 6, 7)
        ]

        return vertices, faces

    def _create_nose(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        y_pos = -0.5
        z_pos = 3.5
        size = 0.3

        vertices = [
            (-size, y_pos - size, z_pos),
            (size, y_pos - size, z_pos),
            (size, y_pos + size, z_pos),
            (-size, y_pos + size, z_pos),
            (-size, y_pos - size, z_pos + size),
            (size, y_pos - size, z_pos + size),
            (size, y_pos + size, z_pos + size),
            (-size, y_pos + size, z_pos + size)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_left_ear(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        x_pos = -1.5
        y_pos = 1.5
        z_pos = 0.5

        w, h, d = 0.6, 0.5, 0.4

        vertices = [
            (x_pos - w, y_pos, z_pos - d),
            (x_pos + w, y_pos, z_pos - d),
            (x_pos + w, y_pos + h, z_pos - d),
            (x_pos - w, y_pos + h, z_pos - d),
            (x_pos - w, y_pos, z_pos + d),
            (x_pos + w, y_pos, z_pos + d),
            (x_pos + w, y_pos + h, z_pos + d),
            (x_pos - w, y_pos + h, z_pos + d)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_right_ear(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        x_pos = 1.5
        y_pos = 1.5
        z_pos = 0.5

        w, h, d = 0.6, 0.5, 0.4

        vertices = [
            (x_pos - w, y_pos, z_pos - d),
            (x_pos + w, y_pos, z_pos - d),
            (x_pos + w, y_pos + h, z_pos - d),
            (x_pos - w, y_pos + h, z_pos - d),
            (x_pos - w, y_pos, z_pos + d),
            (x_pos + w, y_pos, z_pos + d),
            (x_pos + w, y_pos + h, z_pos + d),
            (x_pos - w, y_pos + h, z_pos + d)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_left_eye(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        x_pos = -0.8
        y_pos = 0.5
        z_pos = 2.2

        size = 0.25

        vertices = [
            (x_pos - size, y_pos - size, z_pos - size),
            (x_pos + size, y_pos - size, z_pos - size),
            (x_pos + size, y_pos + size, z_pos - size),
            (x_pos - size, y_pos + size, z_pos - size),
            (x_pos - size, y_pos - size, z_pos + size),
            (x_pos + size, y_pos - size, z_pos + size),
            (x_pos + size, y_pos + size, z_pos + size),
            (x_pos - size, y_pos + size, z_pos + size)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_right_eye(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        x_pos = 0.8
        y_pos = 0.5
        z_pos = 2.2

        size = 0.25

        vertices = [
            (x_pos - size, y_pos - size, z_pos - size),
            (x_pos + size, y_pos - size, z_pos - size),
            (x_pos + size, y_pos + size, z_pos - size),
            (x_pos - size, y_pos + size, z_pos - size),
            (x_pos - size, y_pos - size, z_pos + size),
            (x_pos + size, y_pos - size, z_pos + size),
            (x_pos + size, y_pos + size, z_pos + size),
            (x_pos - size, y_pos + size, z_pos + size)
        ]

        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
            (0, 1, 5), (0, 5, 4),
            (3, 2, 6), (3, 6, 7)
        ]

        return vertices, faces

    def _create_whiskers(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        vertices = []
        faces = []

        y_base = -0.5
        z_base = 2.8

        whisker_length = 1.5
        whisker_thickness = 0.08

        whisker_positions = [
            (-1.0, y_base + 0.3),
            (-1.0, y_base),
            (-1.0, y_base - 0.3),
            (1.0, y_base + 0.3),
            (1.0, y_base),
            (1.0, y_base - 0.3)
        ]

        for x, y in whisker_positions:
            if x < 0:
                x_start = x
                x_end = x - whisker_length
            else:
                x_start = x
                x_end = x + whisker_length

            base_idx = len(vertices)

            vertices.extend([
                (x_start, y - whisker_thickness, z_base - whisker_thickness),
                (x_end, y - whisker_thickness, z_base - whisker_thickness),
                (x_end, y + whisker_thickness, z_base - whisker_thickness),
                (x_start, y + whisker_thickness, z_base - whisker_thickness),
                (x_start, y - whisker_thickness, z_base + whisker_thickness),
                (x_end, y - whisker_thickness, z_base + whisker_thickness),
                (x_end, y + whisker_thickness, z_base + whisker_thickness),
                (x_start, y + whisker_thickness, z_base + whisker_thickness)
            ])

            faces.extend([
                (base_idx + 0, base_idx + 1, base_idx + 2),
                (base_idx + 0, base_idx + 2, base_idx + 3),
                (base_idx + 4, base_idx + 5, base_idx + 6),
                (base_idx + 4, base_idx + 6, base_idx + 7),
                (base_idx + 0, base_idx + 3, base_idx + 7),
                (base_idx + 0, base_idx + 7, base_idx + 4),
                (base_idx + 1, base_idx + 5, base_idx + 6),
                (base_idx + 1, base_idx + 6, base_idx + 2),
                (base_idx + 0, base_idx + 1, base_idx + 5),
                (base_idx + 0, base_idx + 5, base_idx + 4),
                (base_idx + 3, base_idx + 2, base_idx + 6),
                (base_idx + 3, base_idx + 6, base_idx + 7)
            ])

        return vertices, faces

    def get_face_colors(self) -> List[Tuple[float, float, float]]:
        return self.face_colors
