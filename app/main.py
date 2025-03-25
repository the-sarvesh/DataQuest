import streamlit as st
from state_manager import StateManager
from nl2sql_interface import NL2SQLInterface
from visualization_interface import VisualizationInterface
from optimizer_interface import OptimizerInterface
from health_monitor_interface import HealthMonitorInterface
from dotenv import load_dotenv
import os

load_dotenv()

# App Configuration
st.set_page_config(page_title="AI Oracle Assistant", layout="wide")

def connection_form(state):
    with st.form("connection"):
        st.subheader("Database Connection")
        username = st.text_input("Username", "HR")
        password = st.text_input("Password", type="password")
        hostname = st.text_input("Hostname", "Vivobook")
        port = st.number_input("Port", min_value=1, max_value=65535, value=1521)
        service_name = st.text_input("Service Name/SID", "xepdb1")

        if st.form_submit_button("Connect"):
            # Initialize OracleManager with the provided details
            oracle_manager = state.get_state("oracle_class")(hostname, int(port), service_name)
            if oracle_manager.connect(username, password):
                st.success("Connected successfully")
                state.update_state("oracle", oracle_manager)
                state.update_state("visualizer", state.get_state("visualizer_class")(oracle_manager))
                st.experimental_rerun()  # Refresh the page
            else:
                st.error("Connection failed")

def main():
    state = StateManager()
    state.init_state()

    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("DataQuest : AI-Powered Database Assistant") 
        st.write("Welcome to the AI Oracle Assistant! This application allows you to interact with your Oracle database using natural language queries and data visualization tools.")

    if not state.get_state("oracle").conn:
        connection_form(state)
    else:
        tabs = st.tabs(["NL2SQL", "Data Visualization", "Optimizer", "Health Monitor"])
        
        with tabs[0]:
            NL2SQLInterface(state).render()
        
        with tabs[1]:
            VisualizationInterface(state).render()
        
        with tabs[2]:
            OptimizerInterface(state).render()
        
        with tabs[3]:
            HealthMonitorInterface(state).render()

        with col2:
            llm_options = [
                "qwen-2.5-coder-32b",
                "mistral-saba-24b",
                "llama-3.3-70b-specdec",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
            selected_llm = st.selectbox(
                "Select LLM",
                options=llm_options,
                index=llm_options.index("qwen-2.5-coder-32b"),
                key="llm_selector"
            )
            if selected_llm != state.get_state("selected_llm"):
                state.update_state("selected_llm", selected_llm)
                state.update_state("groq", state.get_state("groq_class")(selected_llm))
            
            ddl_dml_enabled = st.checkbox("Enable DDL/DML", value=False, key="ddl_dml_checkbox")
            state.update_state("ddl_dml_enabled", ddl_dml_enabled)

        if st.button("Disconnect"):
            state.get_state("oracle").close()
            st.experimental_rerun()

if __name__ == "__main__":
    main()