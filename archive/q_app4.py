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
        if conn:
            conn.close()

def update_current_aya(aya_id):
    """Update the current aya in the database"""
    print(f"\n=== Updating current aya to {aya_id} ===")
    conn = None
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
        if conn:
            conn.close()

def get_current_aya():
    """Get the current aya from the database"""
    print("\n=== Getting current aya ===")
    conn = None
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
        if conn:
            conn.close()

def load_aya_data():
    """Load aya data from SQLite database"""
    print("\n=== Loading aya data ===")
    conn = None
    try:
        conn = sqlite3.connect('aya.db')
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
            'audio': os.path.join('q_files', row[1]),
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
    finally:
        if conn:
            conn.close()

def main(page: Page):
    print("\n=== Starting Quran Audio Image App ===")
    page.title = "Quran Audio Image App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.theme_mode = "light"

    try:
        # Initialize database and load data
        init_db()
        aya_data = load_aya_data()
        if not aya_data:
            raise ValueError("No aya data found in database")
        current_index = get_current_aya() - 1

        status_text = Text(
            f"Surah {aya_data[current_index]['sura_name']} - Ayah {aya_data[current_index]['aya']}", 
            size=16,
            weight="bold"
        )

        audio_player = Audio(
            src=aya_data[current_index]['audio'],
            autoplay=False,
            volume=1.0
        )
        page.overlay.append(audio_player)

        img_display = Image(
            src=aya_data[current_index]['image'],
            fit=flet.ImageFit.CONTAIN,
            width=400,
            height=400,
            border_radius=10
        )

        def play_current(e=None):
            """Play the current aya"""
            print("Playing current aya")
            # Force a pause before playing to ensure clean state
            audio_player.pause()
            page.update()
            # Now play
            audio_player.play()
            page.update()

        suffix_text = Text(
            str(aya_data[current_index]['aya_suffix']) if aya_data[current_index]['aya_suffix'] else "",
            size=24,
            weight="bold",
            text_align="center"
        )

        def update_content():
            """Update the UI content"""
            print(f"\n=== Updating content for index {current_index} ===")
            
            # Create new audio player with correct source
            nonlocal audio_player
            new_audio = Audio(
                src=aya_data[current_index]['audio'],
                autoplay=False,
                volume=1.0
            )
            
            # Update overlay with new audio player
            page.overlay.clear()
            page.overlay.append(new_audio)
            new_audio.on_state_changed = on_audio_state_changed
            audio_player = new_audio
            
            # Update image and text
            img_display.src = aya_data[current_index]['image']
            suffix = aya_data[current_index]['aya_suffix']
            print(f"Current aya: {aya_data[current_index]['aya']}, Suffix: {suffix}")  # Debug print
            suffix_display = f" - {suffix}" if suffix else ""
            status_text.value = f"Surah {aya_data[current_index]['sura_name']} - Ayah {aya_data[current_index]['aya']}{suffix_display}"
            
            # Update database
            update_current_aya(aya_data[current_index]['id'])
            
            # Update the page
            page.update()
            print("Content update complete")

        def next_item_and_play(e=None):
            """Move to next item and play it"""
            nonlocal current_index
            current_index = (current_index + 1) % len(aya_data)
            print(f"Moving to next item and playing, new index: {current_index}")
            
            # First update the content
            update_content()
            
            # Call play_current function
            play_current()

        def prev_item(e=None):
            """Move to previous item without playing"""
            nonlocal current_index
            current_index = (current_index - 1) % len(aya_data)
            print(f"Moving to previous item, new index: {current_index}")
            update_content()

        def on_audio_state_changed(e):
            """Handle audio state changes"""
            if e.data == "completed":
                # When audio finishes playing, automatically move to next
                next_item_and_play()

        audio_player.on_state_changed = on_audio_state_changed

        # Main layout with all three buttons
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
                                on_click=play_current,
                                tooltip="Play Current"
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