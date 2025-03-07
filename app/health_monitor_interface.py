import streamlit as st
import numpy as np

class HealthMonitorInterface:
    def __init__(self, state_manager):
        self.state = state_manager

    def render(self):
        if st.button("Run Health Check"):
            data = np.random.rand(100, 1)  # Replace with real metrics if available
            self.state.get_state("monitor").train_model(data)
            anomalies = self.state.get_state("monitor").detect_anomalies(data)
            st.write("Anomaly Detection Results:", anomalies)