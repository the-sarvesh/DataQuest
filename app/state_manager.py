import streamlit as st
from oracle_manager import OracleManager
from data_visualizer import DataVisualizer
from groq_handler import GroqHandler
from security import SecurityManager
from health_monitor import HealthMonitor
from dotenv import load_dotenv
import os

load_dotenv()

class StateManager:
    def init_state(self):
        if "oracle" not in st.session_state:
            st.session_state.oracle = OracleManager(os.getenv("ORACLE_DSN"))
        if "generated_sql" not in st.session_state:
            st.session_state.generated_sql = None
        if "executed_sql" not in st.session_state:
            st.session_state.executed_sql = None
        if "query_df" not in st.session_state:
            st.session_state.query_df = None
        # Initialize chat-related state variables
        if "chat_user_question" not in st.session_state:
            st.session_state.chat_user_question = ""
        if "chat_ai_response" not in st.session_state:
            st.session_state.chat_ai_response = ""
        if "chat_has_response" not in st.session_state:
            st.session_state.chat_has_response = False
        # Initialize analysis state
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "show_analysis" not in st.session_state:
            st.session_state.show_analysis = False
        # Initialize visualization-related state variables
        if "query_df_viz" not in st.session_state:
            st.session_state.query_df_viz = None
        if "viz_sql" not in st.session_state:
            st.session_state.viz_sql = None
        # Initialize components
        if "groq_class" not in st.session_state:
            st.session_state.groq_class = GroqHandler
        if "selected_llm" not in st.session_state:
            st.session_state.selected_llm = "qwen-2.5-coder-32b"  # Default LLM
        if "groq" not in st.session_state:
            st.session_state.groq = GroqHandler(st.session_state.selected_llm)
        if "security" not in st.session_state:
            st.session_state.security = SecurityManager()
        if "monitor" not in st.session_state:
            st.session_state.monitor = HealthMonitor()
        # Store DataVisualizer class for instantiation after connection
        if "visualizer_class" not in st.session_state:
            st.session_state.visualizer_class = DataVisualizer
        # Initialize visualizer if oracle is connected
        if "visualizer" not in st.session_state and "oracle" in st.session_state:
            st.session_state.visualizer = DataVisualizer(st.session_state.oracle)
        # Initialize DDL/DML control state
        if "ddl_dml_enabled" not in st.session_state:
            st.session_state.ddl_dml_enabled = False
        if "ddl_dml_output" not in st.session_state:
            st.session_state.ddl_dml_output = None

    def get_state(self, key):
        return st.session_state.get(key)

    def update_state(self, key, value):
        st.session_state[key] = value