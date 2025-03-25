import streamlit as st

class ChatAnalyzer:
    def __init__(self, state_manager):
        self.state = state_manager
        self.row_limit = 200  # Define row limit for LLM context

    def show_chat_section(self):
        """Displays the chat section for interacting with the AI."""
        st.subheader("Chat with AI About the Database Output")

        if "executed_sql" not in st.session_state or "query_df" not in st.session_state:
            st.error("No query context available. Please execute a query first.")
            return

        sql = self.state.get_state("executed_sql")
        df = self.state.get_state("query_df")

        chat_container = st.container()
        
        with chat_container:
            with st.form(key="chat_form"):
                user_question = st.text_input(
                    "Ask a question about the data:", 
                    value=self.state.get_state("chat_user_question"),
                    key="chat_question_input"
                )
                submit_button = st.form_submit_button("Ask")
            
            if submit_button and user_question:
                self.state.update_state("chat_user_question", user_question)
                chat_prompt = self.create_chat_prompt(sql, df, user_question)
                
                with st.spinner("Processing your question..."):
                    try:
                        chat_response = self.state.get_state("groq").analyze_data(chat_prompt)
                        if chat_response:
                            self.state.update_state("chat_ai_response", chat_response)
                            self.state.update_state("chat_has_response", True)
                        else:
                            st.error("No response received from AI.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if self.state.get_state("chat_has_response") and self.state.get_state("chat_ai_response").strip() != "":
                st.subheader("Chat Response")
                st.markdown(self.state.get_state("chat_ai_response"))
                
                if st.button("Clear response", key="clear_chat"):
                    self.state.update_state("chat_has_response", False)
                    self.state.update_state("chat_ai_response", "")
                    st.experimental_rerun()

    def create_chat_prompt(self, sql, df, user_question):
        """Creates the prompt for the AI chat based on the executed SQL and its results."""
        limited_df = df.head(self.row_limit) if len(df) > self.row_limit else df
        if len(df) > self.row_limit:
            st.warning(f"Data context size is high ({len(df)} rows). Chat response is based on the first {self.row_limit} rows only.")
        
        return f"""
        **Task**: Answer the user's question using the SQL query results below. Follow these steps:
        1. Directly answer the question in natural language.
        2. If relevant, provide an Oracle 21c SQL query to explore further.
        3. Format SQL with ```sql code blocks```.

        **Executed SQL**:
        {sql}

        **Query Results (limited to {self.row_limit} rows if larger)**:
        {limited_df.to_string()}

        **Question**:
        {user_question}
        """