import streamlit as st

class VisualizationInterface:
    def __init__(self, state_manager):
        self.state = state_manager

    def render(self):
        if self.state.get_state("visualizer"):
            self.state.get_state("visualizer").display_visualization_interface()
        else:
            st.error("Visualizer not initialized. Please reconnect to the database.")