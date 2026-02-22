#!/usr/bin/env python3
"""
Rat Assistant - Main Entry Point
LLM-powered conversational agent with animated rat avatar.
"""

import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.orchestrator import main

if __name__ == "__main__":
    main()
