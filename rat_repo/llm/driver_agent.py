"""
Driver Agent
Core conversational agent that processes user input and generates responses.
"""

from typing import List, Dict, Optional
from openai import OpenAI
from .config import AgentConfig


def _extract_response_text(response) -> str:
    if getattr(response, "output_text", None):
        return response.output_text

    try:
        for item in response.output:
            for content in item.content:
                if getattr(content, "type", None) == "output_text" and getattr(content, "text", None):
                    return content.text
    except Exception:
        pass

    return ""


class DriverAgent:
    """
    Core driver agent that handles the main conversation flow.
    This is the primary LLM that generates responses to user input.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the driver agent.
        
        Args:
            config: Agent configuration including API key and model settings
        """
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = config.driver_system_prompt
        
        # Initialize with system prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: The user's message
            
        Returns:
            The agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        try:
            response = self.client.responses.create(
                model=self.config.model,
                input=self.conversation_history
            )

            assistant_message = _extract_response_text(response)
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(f"Driver Agent Error: {error_msg}")
            return "I apologize, but I'm having trouble processing that right now."
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, prompt: str):
        """
        Update the system prompt and reset conversation.
        
        Args:
            prompt: New system prompt
        """
        self.system_prompt = prompt
        self.reset_conversation()
