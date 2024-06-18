import sqlite3
import pandas as pd
import argparse

def export_sqlite_to_csv(database_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_file)
    
    try:
        # Export top table to CSV
        top_query = "SELECT * FROM top"
        df_top = pd.read_sql_query(top_query, conn)
        df_top.to_csv('trace_summary.csv', index=False)
    
    finally:
        # Close the database connection
        conn.close()

## Example
# export_sqlite_to_csv('trace.rpd')
