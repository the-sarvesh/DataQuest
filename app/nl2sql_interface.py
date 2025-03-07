import streamlit as st
from query_handler import QueryHandler
from chat_analyzer import ChatAnalyzer
import pandas as pd
import io

class NL2SQLInterface:
    def __init__(self, state_manager):
        self.state = state_manager
        self.query_handler = QueryHandler(self.state)
        self.chat_analyzer = ChatAnalyzer(self.state)

    def render(self):
        col1, col2 = st.columns([3, 2])

        with col1:
            query = st.text_area("Enter your request:", height=150)
            if st.button("Generate SQL"):
                if query:
                    with st.spinner("Generating..."):
                        generated = self.state.get_state("groq").generate_sql(query)
                        self.state.update_state("generated_sql", generated)
                        self.state.update_state("edited_sql", generated)  # Initialize editable SQL
        with col2:
            if self.state.get_state("generated_sql"):
                st.subheader("Generated SQL")
                st.code(self.state.get_state("generated_sql"))
                exe_gen_sql = st.button("Execute Generated SQL")

        st.subheader("Edit & Execute SQL")
        edited_sql = st.text_area(
            "Modify the SQL below:",
            value=self.state.get_state("generated_sql") if self.state.get_state("generated_sql") else "",
            height=150,
            key="edited_sql"
        )

        if st.button("Execute Edited SQL"):
            self.query_handler.execute_query(edited_sql)

        if 'exe_gen_sql' in locals() and exe_gen_sql:
            self.query_handler.execute_query(self.state.get_state("generated_sql"))

        # Display DDL/DML output below the text box if available
        if self.state.get_state("ddl_dml_output"):
            st.subheader("DDL/DML Execution Output")
            st.write(self.state.get_state("ddl_dml_output"))

        # Display query results and analysis/chat only in the NL2SQL tab
        if self.state.get_state("query_df") is not None and self.state.get_state("executed_sql") is not None:
            st.subheader("Query Results")
            st.dataframe(self.state.get_state("query_df"))
            
            # Download button for Excel file
            excel_buffer = io.BytesIO()
            self.state.get_state("query_df").to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)
            st.download_button(
                label="Download Results as Excel",
                data=excel_buffer,
                file_name="query_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel"
            )

            # Four buttons for split analysis (adjusted to 3 as per your code)
            st.subheader("Analyze Data")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Insights"):
                    self.query_handler.generate_insights()
            with col2:
                if st.button("Additional SQL Queries"):
                    self.query_handler.generate_sql_queries()
            with col3:
                if st.button("Visualization Suggestions"):
                    self.query_handler.generate_visualizations()

            # Display stacked results
            if self.state.get_state("analysis_results"):
                st.subheader("Analysis Results")
                for result_type, result_content in self.state.get_state("analysis_results"):
                    st.write(f"**{result_type}**")
                    st.write(result_content)
                
                if st.button("Clear Analysis"):
                    self.state.update_state("analysis_results", None)
                    st.experimental_rerun()
            
            self.chat_analyzer.show_chat_section()