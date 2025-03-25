import cx_Oracle
from typing import Optional, List, Dict
import pandas as pd

class OracleManager:
    def __init__(self, host: str, port: int, service_name: str):
        self.host = host
        self.port = port
        self.service_name = service_name
        self.conn = None

    def connect(self, username: str, password: str) -> bool:
        """Establish connection to Oracle database."""
        try:
            self.conn = cx_Oracle.connect(
                user=username,
                password=password,
                dsn=cx_Oracle.makedsn(
                    self.host,
                    self.port,
                    service_name=self.service_name
                )
            )
            print("Connection successful.")
            return True

        except cx_Oracle.DatabaseError as e:
            error = e.args[0]
            print(f"Oracle Connection Error: ORA-{error.code}: {error.message}")
            return False
        except ValueError as e:
            print(f"Invalid connection parameters: {str(e)}")
            return False
        except Exception as e:
            print(f"General Connection Error: {str(e)}")
            return False

    # Rest of the methods remain unchanged
    def execute_query(self, sql: str) -> pd.DataFrame:
        try:
            if not self.conn:
                raise Exception("No active connection to the database.")
            sql = sql.rstrip(";")
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    return pd.DataFrame(cursor.fetchall(), columns=columns)
                return pd.DataFrame()
        except cx_Oracle.DatabaseError as e:
            error = e.args[0]
            raise Exception(f"Oracle Execution Error: ORA-{error.code}: {error.message}")
        except Exception as e:
            raise Exception(f"General Execution Error: {str(e)}")

    def execute_ddl_dml(self, sql: str) -> str:
        try:
            if not self.conn:
                raise Exception("No active connection to the database.")
            sql = sql.rstrip(";")
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                row_count = cursor.rowcount
                return f"DDL/DML executed successfully. Rows affected: {row_count}"
        except cx_Oracle.DatabaseError as e:
            error = e.args[0]
            raise Exception(f"Oracle Execution Error: ORA-{error.code}: {error.message}")
        except Exception as e:
            raise Exception(f"General Execution Error: {str(e)}")

    def get_performance_data(self) -> List[Dict]:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT sql_id, sql_text, elapsed_time, executions
                    FROM V$SQL 
                    WHERE elapsed_time > 1000000
                    ORDER BY elapsed_time DESC
                """)
                return [
                    dict(zip(["sql_id", "sql_text", "elapsed_time", "executions"], row))
                    for row in cursor.fetchall()
                ]
        except cx_Oracle.DatabaseError as e:
            error = e.args[0]
            print(f"Performance Data Error: ORA-{error.code}: {error.message}")
            return []

    def get_table_metadata(self, sql: str) -> Optional[pd.DataFrame]:
        try:
            table_name = sql.split("FROM")[1].split()[0]
            metadata_query = f"""
                SELECT column_name, data_type, data_length
                FROM all_tab_columns
                WHERE table_name = UPPER('{table_name}')
            """
            with self.conn.cursor() as cursor:
                cursor.execute(metadata_query)
                columns = [col[0] for col in cursor.description]
                return pd.DataFrame(cursor.fetchall(), columns=columns)
        except Exception as e:
            print(f"Error fetching metadata: {str(e)}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()