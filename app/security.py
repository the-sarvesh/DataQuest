import re
from cx_Oracle import DatabaseError
import streamlit as st

class SecurityManager:
    def sanitize_input(self, sql: str) -> bool:
        """
        Sanitizes input SQL based on DDL/DML enablement.
        If disabled, allows only SELECT; if enabled, allows all with basic safety checks.
        """
        sql_upper = sql.upper().strip()
        ddl_dml_enabled = st.session_state.get("ddl_dml_enabled", False)

        if not ddl_dml_enabled:
            # Only allow SELECT statements when DDL/DML is disabled
            if not sql_upper.startswith("SELECT"):
                st.error("Only SELECT statements are allowed when DDL/DML is disabled.")
                return False
        else:
            # When DDL/DML is enabled, apply basic safety checks
            forbidden_patterns = [
                r";\s*--",        # Inline comment after a semicolon
                r"EXEC\s",        # EXEC calls
                r"XP_",           # Extended stored procedures (irrelevant to Oracle)
            ]
            if any(re.search(pattern, sql, re.IGNORECASE) for pattern in forbidden_patterns):
                st.error("Query contains forbidden patterns.")
                return False

        return True