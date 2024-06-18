import sqlite3
import pandas as pd
import argparse

def export_sqlite_to_csv(database_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_file)
    
    try:
        # Export autogradKernel table to CSV
        autograd_query = "SELECT * FROM autogradKernel"
        df_autograd = pd.read_sql_query(autograd_query, conn)
        df_autograd.to_csv('autograd.csv', index=False)

        # Export top table to CSV
        top_query = "SELECT * FROM top"
        df_top = pd.read_sql_query(top_query, conn)
        df_top.to_csv('autograd_from_top.csv', index=False)
    
    finally:
        # Close the database connection
        conn.close()

def process_autograd_data(autograd_summary_file, autograd_from_top_file, output_file):
    # Read the CSV files
    df_auto = pd.read_csv(autograd_summary_file)
    df_top = pd.read_csv(autograd_from_top_file)
    
    # Rename columns in df_auto to align with df_top (or, change kernelName to Name)
    df_auto.columns = ['autogradName', 'Name', 'sizes', 'calls', 'avg_gpu', 'total_gpu']
    # Merge the two dataframes on the 'Name' column
    df_merged = df_top.merge(df_auto, on='Name', how='left')
    # Drop duplicate rows based on the 'Name' column
    df_dedup_name = df_merged.drop_duplicates(subset=['Name'])
    
    # Save the deduplicated dataframe to a CSV file
    df_dedup_name.to_csv(output_file, index=False)

    # Return the deduplicated dataframe
    return df_dedup_name

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Export SQLite tables to CSV and process autograd data.")
    parser.add_argument('database_file', help="Path to the SQLite database file.")
    parser.add_argument('output_file', help="Path to the output CSV file.")
    
    # Parse arguments
    args = parser.parse_args()

    # Export tables to CSV
    export_sqlite_to_csv(args.database_file)

    # Process the exported CSV files
    result_df = process_autograd_data('autograd.csv', 'autograd_from_top.csv', args.output_file)
    
    # Print a success message
    print(f"Data processing complete. Output saved to {args.output_file}")

if __name__ == "__main__":
    main()
