import flet
from flet import IconButton, Page, Row, TextField, icons, Column, Image, Audio, Text, ProgressRing
import csv
import os
from pathlib import Path
import sqlite3
import traceback

def init_db():
    """Initialize the database and create current_aya table if it doesn't exist"""
    print("\n=== Initializing Database ===")
    try:
        conn = sqlite3.connect('aya.db')
        cursor = conn.cursor()
        
        # Create tables if they don't exist using exact DDL
        create_current_aya_sql = '''
        CREATE TABLE IF NOT EXISTS current_aya (
            current_aya INTEGER
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
            cursor.execute('INSERT INTO current_aya (current_aya) VALUES (1)')
        
        conn.commit()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error in init_db: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        raise
    finally:
        conn.close()

def update_current_aya(aya_id):
    """Update the current aya in the database"""
    print(f"\n=== Updating current aya to {aya_id} ===")
    try:
        conn = sqlite3.connect('aya.db')
        cursor = conn.cursor()
        
        # First delete existing row since we only want one row
        cursor.execute('DELETE FROM current_aya')
        
        # Then insert new value
        cursor.execute('INSERT INTO current_aya (current_aya) VALUES (?)', (aya_id,))
        
        conn.commit()
        print("Update successful")
    except Exception as e:
        print(f"Error in update_current_aya: {str(e)}")
        print(traceback.format_exc())
        raise
    finally:
        conn.close()

def get_current_aya():
    """Get the current aya from the database"""
    print("\n=== Getting current aya ===")
    try:
        conn = sqlite3.connect('aya.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT current_aya FROM current_aya LIMIT 1')
        result = cursor.fetchone()
        print(f"Current aya query result: {result}")
        
        if result is None:
            # If no row exists, insert default value 1
            cursor.execute('INSERT INTO current_aya (current_aya) VALUES (1)')
            conn.commit()
            return 1
            
        return result[0]
    except Exception as e:
        print(f"Error in get_current_aya: {str(e)}")
        print(traceback.format_exc())
        raise
    finally:
        conn.close()

def load_aya_data():
    """Load aya data from SQLite database"""
    print("\n=== Loading aya data ===")
    try:
        conn = sqlite3.connect('aya.db')
        cursor = conn.cursor()
        
        select_sql = '''
            SELECT id, audio, image, sura, aya, sura_name 
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
            'audio': os.path.join('q_files', row[1]),
            'image': os.path.join('q_files', row[2]),
            'sura': row[3],
            'aya': row[4],
            'sura_name': row[5]
        } for row in rows]
        
        return result
    except Exception as e:
        print(f"Error in load_aya_data: {str(e)}")
        print(traceback.format_exc())
        raise
    finally:
        conn.close()

def main(page: Page):
    print("\n=== Starting Quran Audio Image App ===")
    page.title = "Quran Audio Image App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.theme_mode = "light"

    try:
        # Initialize database
        print("Initializing database...")
        init_db()

        # Load aya data from database
        print("Loading aya data...")
        aya_data = load_aya_data()
        if not aya_data:
            raise ValueError("No aya data found in database")
        print(f"Loaded {len(aya_data)} ayas")

        # Get the last saved position
        print("Getting current aya position...")
        current_index = get_current_aya() - 1  # Convert to 0-based index
        print(f"Current index: {current_index}")

        # Status text with additional info
        status_text = Text(
            f"Surah {aya_data[current_index]['sura_name']} - Ayah {aya_data[current_index]['aya']}", 
            size=16,
            weight="bold"
        )

        # Initialize audio player
        audio_player = Audio(
            src=aya_data[current_index]['audio'],
            autoplay=False,
            volume=1.0
        )
        page.overlay.append(audio_player)

        # Initialize image display
        img_display = Image(
            src=aya_data[current_index]['image'],
            fit=flet.ImageFit.CONTAIN,
            width=400,
            height=400,
            border_radius=10
        )

        def play_audio(e):
            print("Playing audio")
            audio_player.play()

        def pause_audio(e):
            print("Pausing audio")
            audio_player.pause()

        def next_item(e):
            nonlocal current_index
            current_index = (current_index + 1) % len(aya_data)
            print(f"Moving to next item, new index: {current_index}")
            update_content()

        def prev_item(e):
            nonlocal current_index
            current_index = (current_index - 1) % len(aya_data)
            print(f"Moving to previous item, new index: {current_index}")
            update_content()

        def update_content():
            print(f"\n=== Updating content for index {current_index} ===")
            # Update audio and image
            audio_player.src = aya_data[current_index]['audio']
            img_display.src = aya_data[current_index]['image']
            
            # Update status text with surah name and aya number
            status_text.value = f"Surah {aya_data[current_index]['sura_name']} - Ayah {aya_data[current_index]['aya']}"
            
            # Update current aya in database
            update_current_aya(aya_data[current_index]['id'])
            
            page.update()
            print("Content update complete")

        # Main layout
        page.add(
            Column(
                [
                    status_text,
                    img_display,
                    Row(
                        [
                            IconButton(
                                icons.SKIP_PREVIOUS_ROUNDED,
                                icon_size=30,
                                on_click=prev_item,
                                tooltip="Previous"
                            ),
                            IconButton(
                                icons.PLAY_ARROW_ROUNDED,
                                icon_size=30,
                                on_click=play_audio,
                                tooltip="Play"
                            ),
                            IconButton(
                                icons.PAUSE_ROUNDED,
                                icon_size=30,
                                on_click=pause_audio,
                                tooltip="Pause"
                            ),
                            IconButton(
                                icons.SKIP_NEXT_ROUNDED,
                                icon_size=30,
                                on_click=next_item,
                                tooltip="Next"
                            ),
                        ],
                        alignment="center",
                    ),
                ],
                horizontal_alignment="center",
                spacing=20
            )
        )

    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}"
        print("\n=== ERROR ===")
        print(error_msg)
        print("Detailed traceback:")
        print(traceback.format_exc())
        page.add(Text(error_msg, color="red", size=16, weight="bold"))

if __name__ == "__main__":
    print("\n=== Starting Application ===")
    flet.app(target=main)