import streamlit as st
import pandas as pd
import plotly.express as px

class DataVisualizer:
    def __init__(self, oracle_manager):
        self.oracle_manager = oracle_manager

    def display_visualization_interface(self):
        """Displays the data visualization interface in the Streamlit app."""
        st.subheader("Data Visualization")
        
        # SQL input for visualization
        viz_sql = st.text_area(
            "Enter SQL query for visualization:",
            value=st.session_state.viz_sql if "viz_sql" in st.session_state else "",
            height=100,
            key="viz_sql_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            execute_button = st.button("Execute & Visualize")
        
        if execute_button and viz_sql:
            try:
                from security import SecurityManager
                security = SecurityManager()
                
                if security.sanitize_input(viz_sql):
                    with st.spinner("Executing query..."):
                        df = self.oracle_manager.execute_query(viz_sql)
                        if not df.empty:
                            st.session_state.query_df_viz = df
                            st.session_state.viz_sql = viz_sql
                            st.success("Query executed successfully")
                        else:
                            st.warning("Query returned no data to visualize")
                else:
                    st.error("Query blocked by security rules")
            except Exception as e:
                st.error(f"Execution error: {str(e)}")
        
        # Display the query results in the visualization tab
        if "query_df_viz" in st.session_state and st.session_state.query_df_viz is not None:
            st.subheader("Query Results")
            st.dataframe(st.session_state.query_df_viz)
            
            st.subheader("Create Visualization")
            
            # Get dataframe columns for selection
            df = st.session_state.query_df_viz
            columns = df.columns.tolist()
            
            # Chart type selection
            chart_types = ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot", "Heatmap"]
            chart_type = st.selectbox("Select Chart Type", chart_types)
            
            # Column selections based on chart type
            col1, col2 = st.columns(2)
            
            with col1:
                x_axis = st.selectbox("X-Axis", columns, index=0)
            
            with col2:
                # For pie charts, we need a value column
                if chart_type == "Pie Chart":
                    value_col = st.selectbox("Values", columns, index=min(1, len(columns) - 1))
                # For heatmaps, we need x, y, and value
                elif chart_type == "Heatmap":
                    y_axis = st.selectbox("Y-Axis", columns, index=min(1, len(columns) - 1))
                    color_col = st.selectbox("Value (Color)", columns, index=min(2, len(columns) - 1))
                # For other charts, we can have multiple y-values
                else:
                    y_axis_options = st.multiselect("Y-Axis", columns, default=[columns[min(1, len(columns) - 1)]])
            
            # Additional options
            with st.expander("Chart Options"):
                title = st.text_input("Chart Title", f"{chart_type} of {x_axis}")
                color_discrete = st.color_picker("Base Color", "#1f77b4")
                height = st.slider("Chart Height", 300, 1000, 500)
            
            # Create and display the chart
            if st.button("Generate Chart"):
                with st.spinner("Creating visualization..."):
                    try:
                        fig = self.create_chart(chart_type, df, x_axis, locals())
                        if fig:
                            fig.update_layout(title=title, height=height)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Option to download the chart
                            st.download_button(
                                "Download Chart",
                                fig.to_json(),
                                file_name=f"{title.replace(' ', '_')}.json",
                                mime="application/json"
                            )
                    except Exception as e:
                        st.error(f"Error creating chart: {str(e)}")

    def create_chart(self, chart_type, df, x_axis, options):
        """Creates a Plotly chart based on the selected chart type and options."""
        if chart_type == "Bar Chart":
            y_axis_options = options.get('y_axis_options', [])
            if len(y_axis_options) > 0:
                return px.bar(df, x=x_axis, y=y_axis_options, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
            return px.bar(df, x=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Line Chart":
            y_axis_options = options.get('y_axis_options', [])
            if len(y_axis_options) > 0:
                return px.line(df, x=x_axis, y=y_axis_options, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
            return px.line(df, x=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Scatter Plot":
            y_axis_options = options.get('y_axis_options', [])
            if len(y_axis_options) > 0:
                return px.scatter(df, x=x_axis, y=y_axis_options[0], color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
            return px.scatter(df, x=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Pie Chart":
            value_col = options.get('value_col')
            if value_col:
                return px.pie(df, names=x_axis, values=value_col, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
            return px.pie(df, names=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Histogram":
            return px.histogram(df, x=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Box Plot":
            y_axis_options = options.get('y_axis_options', [])
            if len(y_axis_options) > 0:
                return px.box(df, x=x_axis, y=y_axis_options[0], color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
            return px.box(df, x=x_axis, color_discrete_sequence=[options.get('color_discrete', '#1f77b4')])
        
        elif chart_type == "Heatmap":
            y_axis = options.get('y_axis')
            color_col = options.get('color_col')
            if y_axis and color_col:
                pivot_table = df.pivot_table(values=color_col, index=y_axis, columns=x_axis, aggfunc='mean')
                return px.imshow(pivot_table, color_continuous_scale='Blues')
        
        # Default return if no chart type matches
        return None