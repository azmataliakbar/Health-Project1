import streamlit as st
import time
import asyncio

class StreamlitStreamer:
    """Handles streaming responses in Streamlit"""
    # StreamlitStreamer is responsible for showing live (streamed) text responses in the UI
    # Initialize the streamer with a Streamlit placeholder to display output
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.current_text = ""

    async def update(self, text: str):
        """Update the streamer with new text - now async to match agent expectations"""
        self.current_text = text
        self.placeholder.markdown(self.current_text)
        
        # Use asyncio.sleep instead of time.sleep for async compatibility
        await asyncio.sleep(0.01)

    def complete(self, final_text: str):
        """Complete the streaming with final text - synchronous since no async operations needed"""
        self.current_text = final_text
        self.placeholder.markdown(self.current_text)