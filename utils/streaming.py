import streamlit as st
import time

class StreamlitStreamer:
    """Handles streaming responses in Streamlit"""
    # StreamlitStreamer is responsible for showing live (streamed) text responses in the UI

    # Initialize the streamer with a Streamlit placeholder to display output
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.current_text = ""

    def update(self, text: str):
        self.current_text = text
        self.placeholder.markdown(self.current_text)
        time.sleep(0.01)

    def complete(self, final_text: str):
        self.current_text = final_text
        self.placeholder.markdown(self.current_text)


