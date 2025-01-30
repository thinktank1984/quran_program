import sqlite3
import pandas as pd

def create_and_populate_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('aya.db')
    cursor = conn.cursor()

    # Create all_aya table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_aya (
            id INTEGER PRIMARY KEY,
            audio TEXT,
            image TEXT,
            sura INTEGER,
            aya INTEGER,
            aya_suffix INTEGER,
            sura_name TEXT
        )
    ''')

    # Create current_aya table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_aya (
            current_aya INTEGER
        )
    ''')

    # Insert default value into current_aya
    cursor.execute('INSERT INTO current_aya (current_aya) VALUES (?)', (100,))

    # Read CSV file using pandas
    df = pd.read_csv('sqlite.csv')
    
    # Insert data from DataFrame into all_aya table
    df.to_sql('all_aya', conn, if_exists='replace', index=False)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_and_populate_database()