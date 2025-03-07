import streamlit as st
import pandas as pd

class QueryHandler:
    def __init__(self, state_manager):
        self.state = state_manager

    def execute_query(self, sql):
        """Execute SQL and persist results or output based on type."""
        try:
            if self.state.get_state("security").sanitize_input(sql):
                sql_upper = sql.upper().strip()
                is_ddl_dml = not sql_upper.startswith("SELECT")
                
                if is_ddl_dml and self.state.get_state("ddl_dml_enabled"):
                    # Execute DDL/DML and capture output
                    output = self.state.get_state("oracle").execute_ddl_dml(sql)
                    self.state.update_state("ddl_dml_output", output)
                    # Clear SELECT-related state
                    self.state.update_state("query_df", None)
                    self.state.update_state("executed_sql", None)
                    self.state.update_state("analysis_results", None)
                    st.experimental_rerun()
                else:
                    # Execute SELECT query
                    df = self.state.get_state("oracle").execute_query(sql)
                    if not df.empty:
                        # Store the query context in session state
                        self.state.update_state("executed_sql", sql)
                        self.state.update_state("query_df", df)
                        # Reset analysis and DDL/DML output
                        self.state.update_state("analysis_result", None)
                        self.state.update_state("show_analysis", False)
                        self.state.update_state("analysis_results", None)
                        self.state.update_state("ddl_dml_output", None)
                        st.experimental_rerun()
                    else:
                        self.handle_empty_query(sql)
                        self.state.update_state("ddl_dml_output", None)
            # Error message is handled in sanitize_input for non-SELECT when disabled
        except Exception as e:
            st.error(f"Execution error: {str(e)}")
            if self.state.get_state("ddl_dml_enabled") and not sql_upper.startswith("SELECT"):
                self.state.update_state("ddl_dml_output", f"Error: {str(e)}")

    def handle_empty_query(self, sql):
        """Handles the case where the query returns no rows."""
        metadata = self.state.get_state("oracle").get_table_metadata(sql)
        if metadata is not None:
            st.info("Query executed successfully but returned no rows. Displaying table metadata:")
            st.dataframe(metadata)
        else:
            st.warning("Query executed successfully but returned no rows, and no metadata was available.")

    def _check_context(self):
        """Check if query context exists."""
        if "executed_sql" not in st.session_state or "query_df" not in st.session_state:
            st.error("No query context available for analysis.")
            return False
        return True

    def _append_result(self, result_type, result_content):
        """Append result to the stacked list in session state."""
        if result_content:
            current_results = self.state.get_state("analysis_results") or []
            current_results.append((result_type, result_content))
            self.state.update_state("analysis_results", current_results)

    def generate_insights(self):
        """Generate insights about trends, patterns, or anomalies."""
        if not self._check_context():
            return
        sql = self.state.get_state("executed_sql")
        df = self.state.get_state("query_df")
        prompt = f"""
        Here is the query {sql} executed in Oracle Database 21c, based on that:
        Here is the output from the database:
        {df.to_string()}
        Provide 5 insights sort about trends, patterns or anomalies in this data in points.
        Don't give any sql queries, just insights.
        """
        with st.spinner("Generating insights..."):
            result = self.state.get_state("groq").analyze_data(prompt)
            self._append_result("Insights", result if result else "No insights received from AI.")

    def generate_sql_queries(self):
        """Generate additional SQL queries to dig deeper into the data."""
        if not self._check_context():
            return
        sql = self.state.get_state("executed_sql")
        df = self.state.get_state("query_df")
        prompt = f"""
        Here is the query {sql} executed in Oracle Database 21c, based on that:
        Here is the output from the database:
        {df.to_string()}
        Provide additional Oracle 21c SQL queries to dig deeper into this data, along with a description of their purpose.
        """
        with st.spinner("Generating SQL queries..."):
            result = self.state.get_state("groq").analyze_data(prompt)
            self._append_result("Additional SQL Queries", result if result else "No SQL queries received from AI.")

    def generate_visualizations(self):
        """Generate visualization suggestions."""
        if not self._check_context():
            return
        sql = self.state.get_state("executed_sql")
        df = self.state.get_state("query_df")
        prompt = f"""
        Here is the query {sql} executed in Oracle Database 21c, based on that:
        Here is the output from the database:
        {df.to_string()}
        Suggest visualizations sql (e.g., Bar Chart, Line Chart, Scatter Plot, Pie Chart, Histogram, Box Plot, Heatmap) that might help understand this data better.
        """
        with st.spinner("Generating visualization suggestions..."):
            result = self.state.get_state("groq").analyze_data(prompt)
            self._append_result("Visualization Suggestions", result if result else "No visualization suggestions received from AI.")

    # Kept for compatibility, but not used with the new buttons
    def generate_analysis(self):
        pass

    def create_analysis_prompt(self, sql, df):
        pass