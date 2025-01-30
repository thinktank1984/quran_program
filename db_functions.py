import sqlite3
import os
import traceback
from typing import List, Dict

def init_db(conn: sqlite3.Connection) -> None:
    """Initialize the database and create tables if they don't exist"""
    print("\n=== Initializing Database ===")
    try:
        cursor = conn.cursor()
        
        create_current_aya_sql = '''
        CREATE TABLE IF NOT EXISTS current_aya (
            current_aya INTEGER,
            speed REAL DEFAULT 1.0
        );
        '''
        
        create_all_aya_sql = '''
        CREATE TABLE IF NOT EXISTS all_aya (
            id INTEGER,
            audio TEXT,
            image TEXT,
            sura INTEGER,
            aya INTEGER,
            aya_suffix INTEGER,
            sura_name TEXT
        );
        '''
        
        print("Creating tables if they don't exist...")
        cursor.execute(create_current_aya_sql)
        cursor.execute(create_all_aya_sql)
        
        # Debug: Print existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Existing tables in database: {tables}")
        
        # Check if current_aya is empty
        cursor.execute('SELECT COUNT(*) FROM current_aya')
        count = cursor.fetchone()[0]
        print(f"Number of rows in current_aya: {count}")
        
        if count == 0:
            print("Initializing current_aya with first aya")
            cursor.execute('INSERT INTO current_aya (current_aya, speed) VALUES (1, 1)')
            conn.commit()
        
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error in init_db: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        conn.rollback()
        raise

def load_aya_data(conn: sqlite3.Connection) -> List[Dict]:
    """Load aya data from SQLite database"""
    print("\n=== Loading aya data ===")
    try:
        cursor = conn.cursor()
        
        select_sql = '''
            SELECT id, audio, image, sura, aya, aya_suffix, sura_name 
            FROM all_aya 
            ORDER BY id
        '''
        print(f"Executing SQL: {select_sql}")
        cursor.execute(select_sql)
        
        rows = cursor.fetchall()
        print(f"Number of rows fetched: {len(rows)}")
        if rows:
            print(f"Sample first row: {rows[0]}")
        
        result = [{
            'id': row[0],
            'audio': os.path.abspath(os.path.join('q_files', row[1])),
            'image': os.path.join('q_files', row[2]),
            'sura': row[3],
            'aya': row[4],
            'aya_suffix': row[5],
            'sura_name': row[6]
        } for row in rows]
        
        return result
    except Exception as e:
        print(f"Error in load_aya_data: {str(e)}")
        print(traceback.format_exc())
        raise

def get_current_aya(conn: sqlite3.Connection) -> int:
    """Get the current aya from the database"""
    print("\n=== Getting current aya ===")
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT current_aya FROM current_aya LIMIT 1')
        result = cursor.fetchone()
        print(f"Current aya query result: {result}")
        
        if result is None:
            # If no row exists, insert default values
            conn.execute('BEGIN TRANSACTION')
            cursor.execute('INSERT INTO current_aya (current_aya, speed) VALUES (1, 1.0)')
            conn.commit()
            return 1
            
        return result[0]
    except Exception as e:
        print(f"Error in get_current_aya: {str(e)}")
        print(traceback.format_exc())
        conn.rollback()
        raise

def get_speed(conn: sqlite3.Connection) -> float:
    """Get the current speed from the database"""
    print("\n=== Getting current speed ===")
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT speed FROM current_aya LIMIT 1')
        result = cursor.fetchone()
        print(f"Current speed query result: {result}")
        
        if result is None:
            # If no row exists, insert default values
            conn.execute('BEGIN TRANSACTION')
            cursor.execute('INSERT INTO current_aya (current_aya, speed) VALUES (1, 1.0)')
            conn.commit()
            return 1.0
            
        return float(result[0])
    except Exception as e:
        print(f"Error in get_speed: {str(e)}")
        print(traceback.format_exc())
        conn.rollback()
        raise

def update_speed(conn: sqlite3.Connection, speed: float) -> None:
    """Update the speed in the database"""
    print(f"\n=== Updating speed to {speed} ===")
    try:
        conn.execute('BEGIN TRANSACTION')
        cursor = conn.cursor()
        
        # Check if row exists
        cursor.execute('SELECT COUNT(*) FROM current_aya')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # If no row exists, insert new row
            cursor.execute('INSERT INTO current_aya (current_aya, speed) VALUES (1, ?)', (speed,))
        else:
            # Update existing row
            cursor.execute('UPDATE current_aya SET speed = ?', (speed,))
        
        conn.commit()
        print("Speed update successful")
    except Exception as e:
        print(f"Error in update_speed: {str(e)}")
        print(traceback.format_exc())
        conn.rollback()
        raise

def update_current_aya(conn: sqlite3.Connection, aya_id: int) -> None:
    """Update the current aya in the database"""
    print(f"\n=== Updating current aya to {aya_id} ===")
    try:
        conn.execute('BEGIN TRANSACTION')
        cursor = conn.cursor()
        
        # Check if row exists
        cursor.execute('SELECT COUNT(*) FROM current_aya')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # If no row exists, insert new row
            cursor.execute('INSERT INTO current_aya (current_aya, speed) VALUES (?, 1.0)', (aya_id,))
        else:
            # Update existing row
            cursor.execute('UPDATE current_aya SET current_aya = ?', (aya_id,))
        
        conn.commit()
        print("Update successful")
    except Exception as e:
        print(f"Error in update_current_aya: {str(e)}")
        print(traceback.format_exc())
        conn.rollback()
        raise
