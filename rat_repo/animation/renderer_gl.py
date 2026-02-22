"""
3D Frame Renderer using ModernGL
Provides hardware-accelerated rendering with proper Z-buffering.
"""

import numpy as np
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry
import time
import random
from typing import Optional, Generator
import sys

try:
    from .animation_system import Frame2D, AnimationSystem
    from .behavior_script import BehaviorScript
except ImportError:
    from animation_system import Frame2D, AnimationSystem
    from behavior_script import BehaviorScript


# Vertex Shader - transforms vertices and passes data to fragment shader
VERTEX_SHADER = """
#version 330

uniform mat4 projection;
uniform mat4 view;

in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;

out vec3 frag_pos;
out vec3 frag_normal;
out vec3 frag_color;

void main() {
    gl_Position = projection * view * vec4(in_position, 1.0);
    frag_pos = in_position;
    frag_normal = in_normal;
    frag_color = in_color;
}
"""

# Fragment Shader - calculates final pixel color with lighting
FRAGMENT_SHADER = """
#version 330

in vec3 frag_pos;
in vec3 frag_normal;
in vec3 frag_color;

out vec4 out_color;

uniform vec3 light_direction;
uniform float ambient_strength;

void main() {
    // Normalize the normal vector
    vec3 norm = normalize(frag_normal);
    
    // Calculate directional light intensity
    vec3 light_dir = normalize(light_direction);
    float diff = max(dot(norm, light_dir), 0.0);
    
    // Combine ambient and diffuse lighting
    float intensity = ambient_strength + (1.0 - ambient_strength) * diff;
    
    // Apply lighting to color
    vec3 final_color = frag_color * intensity;
    
    out_color = vec4(final_color, 1.0);
}
"""

# Particle shaders - render colored points in world space
PARTICLE_VERTEX_SHADER = """
#version 330

uniform mat4 projection;
uniform mat4 view;
uniform float point_size;

in vec3 in_position;
in vec3 in_color;

out vec3 frag_color;

void main() {
    gl_Position = projection * view * vec4(in_position, 1.0);
    gl_PointSize = point_size;
    frag_color = in_color;
}
"""

PARTICLE_FRAGMENT_SHADER = """
#version 330

in vec3 frag_color;

out vec4 out_color;

void main() {
    out_color = vec4(frag_color, 1.0);
}
"""


class ParticleSystem:
    """Simple particle system for lightweight emotion effects."""

    def __init__(self):
        self.particles = []
        self.elapsed = 0.0
        self.duration = 0.0
        self.point_size = 6.0

    def start(self, effect_type: str, duration: float, seed: int):
        random.seed(seed)
        self.particles = []
        self.elapsed = 0.0
        self.duration = duration

        if effect_type == "stars":
            self.point_size = 12.0
            count = 90
            for _ in range(count):
                angle = random.uniform(0, 2 * np.pi)
                speed = random.uniform(0.8, 2.0)
                position = np.array([
                    random.uniform(-0.6, 0.6),
                    random.uniform(1.6, 2.6),
                    random.uniform(-2.0, -1.2)
                ], dtype=float)
                velocity = np.array([
                    np.cos(angle) * speed,
                    random.uniform(0.6, 1.6),
                    np.sin(angle) * speed * 0.8
                ], dtype=float)
                color = (1.0, random.uniform(0.85, 1.0), random.uniform(0.4, 0.8))
                life = random.uniform(0.8, 1.4)
                self.particles.append({
                    "pos": position,
                    "vel": velocity,
                    "life": life,
                    "color": color
                })
        elif effect_type == "tears":
            self.point_size = 9.0
            count = 70
            left_eye = np.array([-0.7, 1.0, 0.2], dtype=float)
            right_eye = np.array([0.7, 1.0, 0.2], dtype=float)
            for _ in range(count):
                origin = left_eye if random.random() < 0.5 else right_eye
                position = origin + np.array([
                    random.uniform(-0.15, 0.15),
                    random.uniform(-0.05, 0.15),
                    random.uniform(-0.1, 0.1)
                ], dtype=float)
                velocity = np.array([
                    random.uniform(-0.6, 0.6),
                    random.uniform(-2.6, -1.2),
                    random.uniform(-0.2, 0.2)
                ], dtype=float)
                color = (0.4, 0.7, 1.0)
                life = random.uniform(1.0, 1.9)
                self.particles.append({
                    "pos": position,
                    "vel": velocity,
                    "life": life,
                    "color": color
                })

    def update(self, dt: float):
        if not self.particles:
            return

        self.elapsed += dt
        gravity = np.array([0.0, -2.8, 0.0], dtype=float)
        alive = []

        for p in self.particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            p["vel"] = p["vel"] + gravity * dt * 0.4
            p["pos"] = p["pos"] + p["vel"] * dt
            alive.append(p)

        self.particles = alive

    def get_vertex_data(self) -> Optional[np.ndarray]:
        if not self.particles:
            return None

        data = []
        for p in self.particles:
            data.extend([p["pos"][0], p["pos"][1], p["pos"][2],
                         p["color"][0], p["color"][1], p["color"][2]])
        return np.array(data, dtype='f4')


class GLWindow(mglw.WindowConfig):
    """ModernGL window for rendering 3D animations."""
    
    gl_version = (3, 3)
    title = "3D Animation Viewer"
    window_size = (800, 600)
    aspect_ratio = None
    resizable = True
    samples = 4  # MSAA antialiasing
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Enable depth testing (Z-buffer)
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        # Compile shader program
        self.program = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER
        )

        # Particle shader program
        self.particle_program = self.ctx.program(
            vertex_shader=PARTICLE_VERTEX_SHADER,
            fragment_shader=PARTICLE_FRAGMENT_SHADER
        )
        
        # Set lighting parameters
        self.program['light_direction'].value = (0.3, 0.3, 1.0)
        self.program['ambient_strength'].value = 0.3
        
        # Create projection matrix (orthographic)
        self.update_projection()
        
        # Camera view matrix (looking down -Z axis)
        self.program['view'].value = tuple(np.eye(4, dtype='f4').flatten())
        self.particle_program['view'].value = tuple(np.eye(4, dtype='f4').flatten())
        
        # Storage for current frame data
        self.vbo = None
        self.vao = None
        self.vertex_count = 0

        # Particle rendering state
        self.particle_system = ParticleSystem()
        self.particle_vbo = None
        self.particle_vao = None
        self.particle_vertex_count = 0
        self.active_effect_id = None
        
        # Frame data
        self.current_frame = None
        self.frame_generator = None
        self.is_playing = False
        self.show_info = True
        
        # Performance tracking
        self.frame_times = []
        self.last_frame_time = time.time()
        
        # Background color
        self.ctx.clear_color = (0.1, 0.1, 0.1, 1.0)
    
    def update_projection(self):
        """Update projection matrix based on window size."""
        width, height = self.window_size
        aspect = width / height
        
        # Orthographic projection
        # Flip Y axis to match screen coordinates (Y-down instead of Y-up)
        scale = 5.0
        left = -scale * aspect
        right = scale * aspect
        bottom = scale  # Swapped to flip Y
        top = -scale    # Swapped to flip Y
        near = -100.0
        far = 100.0
        
        projection = np.array([
            [2/(right-left), 0, 0, -(right+left)/(right-left)],
            [0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)],
            [0, 0, -2/(far-near), -(far+near)/(far-near)],
            [0, 0, 0, 1]
        ], dtype='f4')
        
        proj = tuple(projection.T.flatten())
        self.program['projection'].value = proj
        self.particle_program['projection'].value = proj
    
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.update_projection()
    
    def set_frame_generator(self, generator: Generator[Frame2D, None, None]):
        """Set the frame generator for animation playback."""
        self.frame_generator = generator
        self.is_playing = True
    
    def update_frame(self, frame: Frame2D):
        """Update the rendered frame."""
        self.current_frame = frame
        
        if frame.transformed_vertices is None:
            return
        
        vertices_3d = frame.transformed_vertices
        faces = frame.faces
        normals = frame.normals
        face_colors = frame.face_colors
        
        # Build vertex data for GPU
        vertex_data = []
        
        for i, face in enumerate(faces):
            if all(0 <= idx < len(vertices_3d) for idx in face):
                # Get face vertices (3D positions)
                v0 = vertices_3d[face[0]]
                v1 = vertices_3d[face[1]]
                v2 = vertices_3d[face[2]]
                
                # Get face normal
                if normals is not None and i < len(normals):
                    normal = normals[i]
                else:
                    normal = np.array([0.0, 0.0, 1.0])
                
                # Get face color
                if face_colors is not None and i < len(face_colors):
                    color = face_colors[i]
                else:
                    color = (0.2, 0.6, 0.9)  # Default blue
                
                # Add triangle data (position, normal, color for each vertex)
                for vertex in [v0, v1, v2]:
                    vertex_data.extend([
                        vertex[0], vertex[1], vertex[2],  # position
                        normal[0], normal[1], normal[2],   # normal
                        color[0], color[1], color[2]        # color
                    ])
        
        if len(vertex_data) == 0:
            self.vertex_count = 0
            return
        
        # Convert to numpy array
        vertex_array = np.array(vertex_data, dtype='f4')
        
        # Create or update VBO
        if self.vbo is None:
            self.vbo = self.ctx.buffer(vertex_array)
            
            # Create VAO (describes buffer layout)
            self.vao = self.ctx.vertex_array(
                self.program,
                [
                    (self.vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')
                ]
            )
        else:
            # Update existing buffer
            self.vbo.orphan(size=len(vertex_array) * 4)
            self.vbo.write(vertex_array)
        
        self.vertex_count = len(vertex_data) // 9  # 9 floats per vertex
    
    def on_render(self, time_elapsed: float, frame_time: float):
        """Render the current frame."""
        # Clear buffers
        self.ctx.clear(0.1, 0.1, 0.1)
        
        # Get next frame if playing
        if self.is_playing and self.frame_generator is not None:
            try:
                frame = next(self.frame_generator)
                self.update_frame(frame)
            except StopIteration:
                self.is_playing = False
                print("\nAnimation complete!")
        
        # Render geometry
        if self.vao is not None and self.vertex_count > 0:
            self.vao.render(moderngl.TRIANGLES, vertices=self.vertex_count)

        # Update and render particles
        if self.current_frame:
            self._update_particles(self.current_frame, frame_time)
            self._render_particles()
        
        # Calculate FPS
        current_time = time.time()
        if self.last_frame_time > 0:
            ft = current_time - self.last_frame_time
            self.frame_times.append(ft)
            if len(self.frame_times) > 30:
                self.frame_times.pop(0)
        self.last_frame_time = current_time
        
        # Display info (using imgui or text overlay would be better, but keeping it simple)
        if self.show_info and self.current_frame:
            avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
            state = self.current_frame.state
            info = (
                f"Frame: {self.current_frame.frame_number} | "
                f"Time: {self.current_frame.timestamp:.2f}s | "
                f"FPS: {avg_fps:.1f} | "
                f"Rot: [{state.rotation[0]:.0f}°, {state.rotation[1]:.0f}°, {state.rotation[2]:.0f}°]"
            )
            self.wnd.title = f"{self.title} - {info}"

    def _update_particles(self, frame: Frame2D, frame_time: float):
        effect_type = frame.metadata.get("effect_type")
        effect_id = frame.metadata.get("effect_id")
        effect_duration = frame.metadata.get("effect_duration", 0.0)
        effect_elapsed = frame.metadata.get("effect_elapsed", 0.0)

        if effect_type and effect_id and effect_elapsed <= effect_duration:
            if effect_id != self.active_effect_id:
                self.active_effect_id = effect_id
                self.particle_system.start(effect_type, effect_duration, seed=hash(effect_id))

        self.particle_system.update(frame_time)

    def _render_particles(self):
        vertex_data = self.particle_system.get_vertex_data()
        if vertex_data is None:
            self.particle_vertex_count = 0
            return

        if self.particle_vbo is None:
            self.particle_vbo = self.ctx.buffer(vertex_data)
            self.particle_vao = self.ctx.vertex_array(
                self.particle_program,
                [(self.particle_vbo, '3f 3f', 'in_position', 'in_color')]
            )
        else:
            self.particle_vbo.orphan(size=len(vertex_data) * 4)
            self.particle_vbo.write(vertex_data)

        self.particle_vertex_count = len(vertex_data) // 6
        self.particle_program['point_size'].value = float(self.particle_system.point_size)
        if self.particle_vao is not None and self.particle_vertex_count > 0:
            self.particle_vao.render(moderngl.POINTS, vertices=self.particle_vertex_count)
    
    def key_event(self, key, action, modifiers):
        """Handle keyboard events."""
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.ESCAPE:
                self.close()
            elif key == self.wnd.keys.SPACE:
                self.is_playing = not self.is_playing
            elif key == self.wnd.keys.I:
                self.show_info = not self.show_info


class GLAnimationPlayer:
    """
    Plays animations using ModernGL with hardware Z-buffering.
    """
    
    def __init__(self, animation_system: AnimationSystem,
                 title: str = "3D Animation Player",
                 width: int = 800,
                 height: int = 600):
        self.animation_system = animation_system
        self.title = title
        self.width = width
        self.height = height
    
    def play(self, script: BehaviorScript, max_frames: Optional[int] = None,
             show_info: bool = True):
        """
        Play an animation using ModernGL renderer.
        """
        print(f"\nPlaying animation with ModernGL renderer...")
        print("Controls:")
        print("  SPACE - Pause/Resume")
        print("  I - Toggle info display")
        print("  ESC - Close window")
        
        # Create frame generator
        frame_generator = self.animation_system.stream_frames(script, max_frames=max_frames)
        
        # Configure window
        GLWindow.title = self.title
        GLWindow.window_size = (self.width, self.height)
        
        # Run the window with our frame generator
        class AnimatedWindow(GLWindow):
            def __init__(inner_self, **kwargs):
                super().__init__(**kwargs)
                inner_self.set_frame_generator(frame_generator)
                inner_self.show_info = show_info
        
        # Run the ModernGL window
        mglw.run_window_config(AnimatedWindow)

    def play_stream(self, frame_generator: Generator[Frame2D, None, None],
                   show_info: bool = True):
        """
        Play a continuous frame stream using ModernGL renderer.
        """
        print("\nPlaying animation with ModernGL renderer...")
        print("Controls:")
        print("  SPACE - Pause/Resume")
        print("  I - Toggle info display")
        print("  ESC - Close window")

        # Configure window
        GLWindow.title = self.title
        GLWindow.window_size = (self.width, self.height)

        # Run the window with our frame generator
        class AnimatedWindow(GLWindow):
            def __init__(inner_self, **kwargs):
                super().__init__(**kwargs)
                inner_self.set_frame_generator(frame_generator)
                inner_self.show_info = show_info

        # Run the ModernGL window
        mglw.run_window_config(AnimatedWindow)


def run_gl_demo():
    """Demo function to test the GL renderer."""
    from face_model import FaceModel
    
    print("\n" + "=" * 50)
    print("MODERNGL RENDERER DEMO")
    print("=" * 50)
    
    # Create model
    face = FaceModel("gl_demo_face")
    
    # Create animation system
    anim_system = AnimationSystem(face, width=800, height=600, fps=30)
    
    # Create behavior script
    script = BehaviorScript()
    script.rotate(0, 360, 0, duration=8.0, easing="linear")
    
    # Play with GL renderer (orientation fix applied automatically)
    player = GLAnimationPlayer(anim_system, title="Face Model - ModernGL", width=800, height=600)
    player.play(script, show_info=True)


if __name__ == "__main__":
    run_gl_demo()
