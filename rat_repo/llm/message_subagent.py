"""
Message Processor Subagent
Processes and refines messages for display to the user.
"""

from typing import Optional
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


class MessageSubagent:
    """
    Subagent responsible for processing and refining messages.
    Takes the driver agent's response and formats it for optimal user experience.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the message subagent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.system_prompt = config.message_system_prompt
    
    def process_message(self, raw_message: str, context: Optional[str] = None) -> str:
        """
        Process and refine a message for display.
        
        Args:
            raw_message: The raw message from the driver agent
            context: Optional context about the conversation
            
        Returns:
            Refined message ready for display
        """
        # For now, we'll do light processing
        # In the future, this could do more sophisticated formatting
        
        prompt = f"Refine this message for clarity and friendliness:\n\n{raw_message}"
        
        if context:
            prompt = f"Context: {context}\n\n" + prompt
        
        try:
            response = self.client.responses.create(
                model=self.config.model,
                input=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            return _extract_response_text(response)
            
        except Exception as e:
            print(f"Message Subagent Error: {str(e)}")
            # Fallback to original message if processing fails
            return raw_message
    
    def format_for_console(self, message: str, max_width: int = 80) -> str:
        """
        Format message for console display with word wrapping.
        
        Args:
            message: Message to format
            max_width: Maximum line width
            
        Returns:
            Formatted message
        """
        words = message.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
