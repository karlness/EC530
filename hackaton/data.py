import sqlite3
import pandas as pd
import os
import time

########################################################################
# GLOBAL SETTINGS
########################################################################

DB_PATH = 'example.db'           # SQLite DB file
ERROR_LOG = 'error_log.txt'      # Error log file


########################################################################
# STEP 1 CODE
########################################################################
def step1_demo(csv_path):
    """
    Step 1:
      - Manually create a simple table in SQLite.
      - Load a CSV via pandas.
      - Insert it into a new table.
      - Run a basic SELECT query.
    """
    conn = sqlite3.connect(DB_PATH)

    # 1) Manually create a "people" table (just for demo)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    ''')
    print("Table 'people' created (if it didn't exist).")

    # 2) Read CSV with pandas
    df = pd.read_csv(csv_path)
    print("DataFrame loaded from CSV. First 5 rows:")
    print(df.head())

    # 3) Insert CSV data into a new table 'mytable'
    df.to_sql('mytable', conn, if_exists='replace', index=False)
    print(f"Data inserted into 'mytable' from {csv_path}.")

    # 4) Run a basic query
    cursor = conn.execute("SELECT * FROM mytable LIMIT 5;")
    rows = cursor.fetchall()
    print("\nSample rows from 'mytable':")
    for row in rows:
        print(row)

    conn.close()
    print("Database connection closed.")


########################################################################
# STEP 2 CODE
########################################################################
def infer_sqlite_type(dtype):
    """
    Simple mapping from pandas dtype to SQLite type.
    """
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    else:
        return "TEXT"

def create_table_from_csv(csv_path, table_name):
    """
    Step 2:
      - Automate table creation by inferring schema from CSV.
      - Create the table using a dynamically generated CREATE TABLE statement.
      - Insert CSV data into that table.
      - Show a few sample rows.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(csv_path)

    # Infer column names and types
    columns = []
    for col in df.columns:
        col_type = infer_sqlite_type(df[col].dtype)
        columns.append(f"\"{col}\" {col_type}")

    # Build CREATE TABLE statement
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  {',\n  '.join(columns)}\n);"

    # Execute CREATE TABLE
    conn.execute(create_table_sql)
    print(f"Executed:\n{create_table_sql}\n")

    # Insert data using to_sql
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Inserted data from {csv_path} into '{table_name}'.")

    # Display sample rows
    cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    rows = cursor.fetchall()
    print("\nSample rows:")
    for row in rows:
        print(row)

    conn.close()


########################################################################
# STEP 3 CODE
########################################################################
def log_error(message):
    """
    Log errors or important messages to an external file (error_log.txt).
    """
    with open(ERROR_LOG, 'a') as f:
        f.write(f"[{time.ctime()}] {message}\n")

def check_table_schema(conn, table_name):
    """
    Returns a list of (column_name, column_type) for the table
    or None if table doesn't exist.
    """
    cursor = conn.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    )
    table_found = cursor.fetchone()
    if not table_found:
        return None
    
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    schema_info = cursor.fetchall()
    # schema_info is a list of tuples: (cid, name, type, notnull, dflt_value, pk)
    return [(col[1], col[2]) for col in schema_info]

def create_or_handle_conflict(csv_path, table_name):
    """
    Step 3:
      - Check if table already exists, compare schema.
      - Prompt user to Overwrite, Rename, or Skip.
      - Log invalid choices.
      - Then create the table with inferred schema if needed.
    """
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(DB_PATH)

    existing_schema = check_table_schema(conn, table_name)
    if existing_schema is not None:
        print(f"Table '{table_name}' already exists with schema:")
        for col_name, col_type in existing_schema:
            print(f"  {col_name} {col_type}")
        
        choice = input("Schema conflict. [O]verwrite / [R]ename / [S]kip? ").strip().upper()
        if choice == 'O':
            # Overwrite
            conn.execute(f"DROP TABLE {table_name};")
            print(f"Dropped table '{table_name}'.")
        elif choice == 'R':
            # Rename the existing table
            new_name = table_name + "_old"
            conn.execute(f"ALTER TABLE {table_name} RENAME TO {new_name};")
            print(f"Renamed table '{table_name}' to '{new_name}'.")
        elif choice == 'S':
            print("Skipping creation.")
            conn.close()
            return
        else:
            print("Invalid choice. Skipping creation.")
            log_error("Invalid schema conflict choice made.")
            conn.close()
            return

    # Infer schema from CSV
    columns = []
    for col in df.columns:
        col_type = infer_sqlite_type(df[col].dtype)
        columns.append(f"\"{col}\" {col_type}")

    create_table_sql = f"CREATE TABLE {table_name} (\n  {',\n  '.join(columns)}\n);"
    conn.execute(create_table_sql)
    print(f"Created table '{table_name}' with inferred schema.")

    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Inserted data into '{table_name}' from {csv_path}.")

    conn.close()


########################################################################
# STEP 4 CODE
########################################################################
def list_tables(conn):
    """
    List all tables in the connected SQLite database.
    """
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables in the database:")
    for t in tables:
        print(f"  - {t}")

def load_csv_into_db(csv_path, table_name, conn):
    """
    Helper function to load CSV into a specified table (replacing if exists).
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"CSV loaded into table '{table_name}' from {csv_path}.")

def run_query(query, conn):
    """
    Run a given SQL query and print the result rows.
    """
    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")

def interactive_cli():
    """
    Step 4:
      - Create a simple CLI loop to interact with the database.
      - Let the user: load CSV, list tables, run SQL queries, or exit.
    """
    conn = sqlite3.connect(DB_PATH)
    print("Connected to the database (Step 4 CLI).")

    while True:
        user_input = input("\nWhat would you like to do? [load/list/run/exit] ").strip().lower()
        
        if user_input == 'load':
            csv_path = input("Enter CSV path: ").strip()
            table_name = input("Enter table name to create/replace: ").strip()
            if os.path.exists(csv_path):
                load_csv_into_db(csv_path, table_name, conn)
            else:
                print(f"CSV file '{csv_path}' does not exist.")
        elif user_input == 'list':
            list_tables(conn)
        elif user_input == 'run':
            query = input("Enter SQL query: ").strip()
            run_query(query, conn)
        elif user_input == 'exit':
            print("Exiting Step 4 CLI...")
            break
        else:
            print("Invalid command. Please choose from [load/list/run/exit].")

    conn.close()


########################################################################
# MAIN MENU / SINGLE ENTRY POINT
########################################################################
def main():
    """
    A simple menu that lets you pick which step to run, combining Steps 1-4.
    (Step 5 AI integration is omitted in this script.)
    """
    while True:
        print("\n====================")
        print("COMBINED STEPS MENU")
        print("====================")
        print("1) Step 1: Manually load CSV & basic queries")
        print("2) Step 2: Create table from CSV (dynamic)")
        print("3) Step 3: Handle schema conflicts")
        print("4) Step 4: CLI for CSV loading & SQL queries")
        print("0) Exit")
        
        choice = input("Select an option [0-4]: ").strip()
        
        if choice == '1':
            csv_path = input("Enter CSV path for Step 1: ").strip()
            if os.path.exists(csv_path):
                step1_demo(csv_path)
            else:
                print(f"File '{csv_path}' not found.")
        elif choice == '2':
            csv_path = input("Enter CSV path for Step 2: ").strip()
            table_name = input("Enter table name to create for Step 2: ").strip()
            if os.path.exists(csv_path):
                create_table_from_csv(csv_path, table_name)
            else:
                print(f"File '{csv_path}' not found.")
        elif choice == '3':
            csv_path = input("Enter CSV path for Step 3: ").strip()
            table_name = input("Enter table name for Step 3: ").strip()
            if os.path.exists(csv_path):
                create_or_handle_conflict(csv_path, table_name)
            else:
                print(f"File '{csv_path}' not found.")
        elif choice == '4':
            interactive_cli()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please try again.")


########################################################################
# ENTRY POINT
########################################################################
if __name__ == "__main__":
    main()
