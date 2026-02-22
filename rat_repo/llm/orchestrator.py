"""
Agent Orchestrator
Main coordination system that manages all agents and the animation display.
"""

import sys
import os
import threading
import queue
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import atexit
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from animation.rat_model import RatModel
from animation.animation_system import AnimationSystem
from animation.renderer_gl import GLAnimationPlayer
from animation.behavior_script import BehaviorScript

from .config import AgentConfig
from .driver_agent import DriverAgent
from .message_subagent import MessageSubagent
from .animation_subagent import AnimationSubagent


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents and manages the animation display.
    Runs the conversation loop and triggers animations based on responses.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Agent configuration (creates default if None)
        """
        self.config = config or AgentConfig.from_env()
        
        # Initialize agents
        print("Initializing agents...")
        self.driver = DriverAgent(self.config)
        self.message_processor = MessageSubagent(self.config)
        self.animation_controller = AnimationSubagent(self.config)
        
        # Animation system components
        self.rat_model = None
        self.animation_system = None
        self.animation_player = None
        
        # Threading for animation
        self.animation_queue = queue.Queue()
        self.animation_thread = None
        self.animation_running = False
        self.stream_running = False
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        self._debug = os.getenv("LLM_DEBUG", "false").lower() in ["1", "true", "yes"]

        atexit.register(self._log_shutdown_state)
        
        print("Orchestrator initialized!")
    
    def initialize_animation_system(self, width: int = 800, height: int = 600, fps: int = 60):
        """
        Initialize the animation system and player.
        
        Args:
            width: Window width
            height: Window height
            fps: Frames per second
        """
        print("Initializing animation system...")
        self.rat_model = RatModel("assistant_rat")
        self.animation_system = AnimationSystem(self.rat_model, width=width, height=height, fps=fps)
        
        # Apply initial orientation (180-degree Z rotation for proper viewing)
        import numpy as np
        self.animation_system.set_state(rotation=np.array([0.0, 0.0, 180.0]))
        self.animation_system.set_base_state()
        
        print("Animation system ready!")
    
    def start_animation_window(self, width: int = 800, height: int = 600):
        """
        Start the animation window in a separate thread.
        
        Args:
            width: Window width
            height: Window height
        """
        if not self.animation_system:
            self.initialize_animation_system(width, height)
        
        self.running = True
        self.animation_running = True
        self.stream_running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        
        # Give the window time to initialize
        time.sleep(1)
    
    def _animation_loop(self):
        """
        Run the animation display loop in a separate thread.
        This continuously checks for new animations to play.
        """
        # Create player
        self.animation_player = GLAnimationPlayer(
            self.animation_system,
            title="Rat Assistant - Press ESC to quit",
            width=800,
            height=600
        )

        try:
            self.animation_player.play_stream(self._frame_stream(), show_info=False)
        except Exception as e:
            print(f"Animation loop error: {e}")
            traceback.print_exc()
        finally:
            self.animation_running = False
            self.stream_running = False
            print("Animation window closed; continuing in console mode.")

    def _log_shutdown_state(self):
        self._log_debug(
            f"Orchestrator shutdown: running={self.running} "
            f"animation_thread_alive={self.animation_thread.is_alive() if self.animation_thread else None}"
        )

    def _log_debug(self, message: str):
        if not self._debug:
            return
        print(f"[DEBUG] {message}")
        sys.stdout.flush()

    def _frame_stream(self):
        """
        Continuous frame generator that plays queued animations and idles between them.
        """
        idle_factory = AnimationSubagent._create_neutral_animation
        self.animation_system.reset_state()
        current_gen = self.animation_system.stream_frames(idle_factory())
        playing_idle = True

        while self.stream_running:
            if playing_idle:
                try:
                    script = self.animation_queue.get_nowait()
                    print(f"Playing queued animation: {script.name}")
                    current_gen = self.animation_system.stream_frames(script)
                    playing_idle = False
                except queue.Empty:
                    pass

            try:
                yield next(current_gen)
            except StopIteration:
                if not playing_idle:
                    playing_idle = True
                    self.animation_system.reset_state()
                current_gen = self.animation_system.stream_frames(idle_factory())
    
    def queue_animation(self, script: BehaviorScript):
        """
        Queue an animation to be played.
        
        Args:
            script: BehaviorScript to play
        """
        self.animation_queue.put(script)
    
    def process_user_input(self, user_input: str) -> dict:
        """
        Process user input through the agent pipeline.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with response and metadata
        """
        print("\n[Processing...]")
        
        # 1. Driver agent generates response
        driver_response = self.driver.process_input(user_input)
        
        # 2. Run animation and message subagents in parallel
        animation_future = self.executor.submit(
            self.animation_controller.analyze_and_animate,
            driver_response
        )
        message_future = self.executor.submit(
            self.message_processor.process_message,
            driver_response
        )

        animation_script = None
        emotion_analysis = {}
        final_message = driver_response

        try:
            message_result = message_future.result()
            if isinstance(message_result, str) and message_result.strip():
                final_message = message_result
        except Exception as e:
            print(f"Subagent error (message): {e}")


        try:
            animation_script, emotion_analysis = animation_future.result()
        except Exception as e:
            print(f"Subagent error (animation): {e}")

        
        # Queue the animation
        if self.stream_running and animation_script is not None:
            self.queue_animation(animation_script)
        
        return {
            "message": final_message,
            "emotion": emotion_analysis.get("emotion", "neutral"),
            "intensity": emotion_analysis.get("intensity", "medium"),
            "animation": animation_script.name if animation_script else None,
            "raw_response": driver_response
        }
    
    def run_console_mode(self):
        """
        Run in console-only mode without animation window.
        Useful for testing the agent logic without graphics.
        """
        print("\n" + "="*60)
        print("RAT ASSISTANT - CONSOLE MODE")
        print("="*60)
        print("Type 'quit' or 'exit' to end the conversation")
        print("="*60 + "\n")
        
        while True:
            # Get user input
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGoodbye!")
                break
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nRat Assistant: Goodbye! Have a great day!")
                break
            
            if not user_input:
                continue
            
            # Process input
            result = self.process_user_input(user_input)
            
            # Display response
            print(f"\nRat Assistant [{result['emotion']}]: {result['message']}")
    
    def run_with_animation(self, width: int = 800, height: int = 600):
        """
        Run with animation window.
        
        Args:
            width: Window width
            height: Window height
        """
        print("\n" + "="*60)
        print("RAT ASSISTANT - ANIMATED MODE")
        print("="*60)
        print("Starting animation window...")
        print("Type 'quit' or 'exit' to end the conversation")
        print("Press ESC in the animation window to close it")
        print("="*60 + "\n")
        
        # Start animation window
        self.start_animation_window(width, height)
        
        print("Animation window started! You can now chat.")
        
        try:
            while self.running:
                self._log_debug("Waiting for user input...")
                # Get user input
                try:
                    user_input = input("\nYou: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\nGoodbye!")
                    break
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nRat Assistant: Goodbye! Have a great day!")
                    break
                
                if not user_input:
                    continue
                
                # Process input
                self._log_debug("Processing user input...")
                result = self.process_user_input(user_input)

                self._log_debug("Response ready; printing message.")
                
                # Display response
                print(f"\nRat Assistant [{result['emotion']}]: {result['message']}")
        except Exception as e:
            print(f"Run loop error: {e}")
            traceback.print_exc()
        
        finally:
            self.running = False
            if self.animation_thread:
                self.animation_thread.join(timeout=2)
            self._log_debug("Run loop exited; running flag set to False.")
    
    def stop(self):
        """Stop the orchestrator and cleanup."""
        self.stream_running = False
        self.running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=2)
        if self.executor:
            self.executor.shutdown(wait=False)

    def start_frame_stream(self, width: int = 800, height: int = 600, fps: int = 60):
        """Start a headless frame stream for external clients."""
        if not self.animation_system:
            self.initialize_animation_system(width=width, height=height, fps=fps)
        else:
            self.animation_system.set_render_size(width, height)
            self.animation_system.fps = fps
            self.animation_system.frame_time = 1.0 / fps
        self.stream_running = True
        return self._frame_stream()


def main():
    """Main entry point for the orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rat Assistant - LLM Agent with Animation")
    parser.add_argument('--console-only', action='store_true', 
                       help='Run in console-only mode without animation')
    parser.add_argument('--width', type=int, default=800, 
                       help='Animation window width')
    parser.add_argument('--height', type=int, default=600, 
                       help='Animation window height')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    try:
        if args.console_only:
            orchestrator.run_console_mode()
        else:
            orchestrator.run_with_animation(width=args.width, height=args.height)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        orchestrator.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
