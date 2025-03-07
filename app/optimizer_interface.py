import streamlit as st

class OptimizerInterface:
    def __init__(self, state_manager):
        self.state = state_manager

    def render(self):
        if st.button("Analyze Slow Queries"):
            queries = self.state.get_state("oracle").get_performance_data()
            for q in queries:
                with st.expander(f"Query {q['sql_id']}"):
                    st.code(q["sql_text"])
                    optimized = self.state.get_state("groq").optimize_sql(q["sql_text"])
                    st.markdown(f"**Optimization Suggestions:**\n{optimized}")