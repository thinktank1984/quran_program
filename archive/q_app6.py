import flet as ft
import traceback
import os
from db_functions import DatabaseConnection, init_db, load_aya_data, get_current_aya, update_current_aya

def main(page: ft.Page):
    print("\n=== Starting Quran Audio Image App ===")
    page.title = "Quran Audio Image App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.theme_mode = "light"

    try:
        # Initialize database connection and store it in the page object
        page.db = DatabaseConnection('aya.db')
        conn = page.db.get_connection()
        
        # Initialize database and load data
        init_db(conn)
        aya_data = load_aya_data(conn)
        if not aya_data:
            raise ValueError("No aya data found in database")
        current_index = get_current_aya(conn) - 1

        # Store important data in page object for persistence
        page.conn = conn
        page.aya_data = aya_data
        page.current_index = current_index

        # Get unique sura names and their first ayah indices
        sura_map = {}
        for item in aya_data:
            if item['sura_name'] not in sura_map:
                sura_map[item['sura_name']] = {
                    'first_index': aya_data.index(item),
                    'last_aya': max(x['aya'] for x in aya_data if x['sura_name'] == item['sura_name'])
                }

        status_text = ft.Text(
            f"Surah {aya_data[current_index]['sura_name']} - Ayah {aya_data[current_index]['aya']}", 
            size=16,
            weight="bold"
        )

        def build_sura_dropdown():
            """Create dropdown for surah selection"""
            sura_dd = ft.Dropdown(
                width=200,
                label="Select Surah",
                value=aya_data[current_index]['sura_name'],
                options=[
                    ft.dropdown.Option(text=sura_name) 
                    for sura_name in sorted(sura_map.keys())
                ],
            )
            return sura_dd

        def build_aya_dropdown(sura_name):
            """Create dropdown for ayah selection"""
            max_aya = sura_map[sura_name]['last_aya']
            aya_dd = ft.Dropdown(
                width=100,
                label="Select Ayah",
                value=str(aya_data[current_index]['aya']),
                options=[
                    ft.dropdown.Option(text=str(i)) 
                    for i in range(1, max_aya + 1)
                ],
            )
            return aya_dd

        # Create dropdowns
        sura_dropdown = build_sura_dropdown()
        aya_dropdown = build_aya_dropdown(aya_data[current_index]['sura_name'])

        audio_player = ft.Audio(
            src=aya_data[current_index]['audio'],
            autoplay=False,
            volume=1.0
        )
        page.overlay.append(audio_player)

        img_display = ft.Image(
            src=aya_data[current_index]['image'],
            width=400,
            height=400,
            fit=ft.ImageFit.CONTAIN,
        )

        def play_current(e=None):
            """Play the current aya"""
            print("Playing current aya")
            audio_player.play()
            page.update()

        def update_content():
            """Update the UI content"""
            print(f"\n=== Updating content for index {page.current_index} ===")
            
            # Create new audio player with correct source
            nonlocal audio_player
            new_audio = ft.Audio(
                src=page.aya_data[page.current_index]['audio'],
                autoplay=False,
                volume=1.0
            )
            
            # Update overlay with new audio player
            page.overlay.clear()
            page.overlay.append(new_audio)
            new_audio.on_state_changed = on_audio_state_changed
            audio_player = new_audio
            
            # Update image and text
            img_display.src = page.aya_data[page.current_index]['image']
            suffix = page.aya_data[page.current_index]['aya_suffix']
            suffix_display = f" - {suffix}" if suffix else ""
            status_text.value = f"Surah {page.aya_data[page.current_index]['sura_name']} - Ayah {page.aya_data[page.current_index]['aya']}{suffix_display}"
            
            # Update dropdown selections
            sura_dropdown.value = page.aya_data[page.current_index]['sura_name']
            aya_dropdown.value = str(page.aya_data[page.current_index]['aya'])
            
            # Update database using the persistent connection
            update_current_aya(page.conn, page.aya_data[page.current_index]['id'])
            
            # Update the page
            page.update()
            print("Content update complete")

        def on_sura_change(e):
            """Handle surah selection change"""
            selected_sura = sura_dropdown.value
            # Update ayah dropdown with new range
            aya_dropdown.options = [
                ft.dropdown.Option(text=str(i)) 
                for i in range(1, sura_map[selected_sura]['last_aya'] + 1)
            ]
            aya_dropdown.value = "1"
            go_to_selection(None)
            page.update()

        def on_aya_change(e):
            """Handle ayah selection change"""
            go_to_selection(e)

        def go_to_selection(e):
            """Navigate to selected ayah"""
            if not sura_dropdown.value or not aya_dropdown.value:
                return

            new_index = find_aya_index(sura_dropdown.value, int(aya_dropdown.value))
            if new_index is not None:
                page.current_index = new_index
                update_content()

        def find_aya_index(sura_name, aya_number):
            """Find the index of a specific ayah in a surah"""
            for i, item in enumerate(page.aya_data):
                if item['sura_name'] == sura_name and item['aya'] == aya_number:
                    return i
            return None

        def next_item_and_play(e=None):
            """Move to next item and play it"""
            page.current_index = (page.current_index + 1) % len(page.aya_data)
            print(f"Moving to next item and playing, new index: {page.current_index}")
            update_content()
            play_current()

        def prev_item(e=None):
            """Move to previous item without playing"""
            page.current_index = (page.current_index - 1) % len(page.aya_data)
            print(f"Moving to previous item, new index: {page.current_index}")
            update_content()

        def on_audio_state_changed(e):
            """Handle audio state changes"""
            if e.data == "completed":
                next_item_and_play()

        # Set up event handlers
        audio_player.on_state_changed = on_audio_state_changed
        sura_dropdown.on_change = on_sura_change
        aya_dropdown.on_change = on_aya_change

        # Add cleanup handler to close database connection
        def cleanup(e):
            if hasattr(page, 'db'):
                page.db.close()
        
        page.on_close = cleanup

        # Add elements to page
        page.add(
            ft.Column(
                [
                    status_text,
                    ft.Row(
                        [sura_dropdown, aya_dropdown],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    img_display,
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.SKIP_PREVIOUS,
                                icon_size=30,
                                on_click=prev_item,
                            ),
                            ft.IconButton(
                                icon=ft.icons.PLAY_ARROW,
                                icon_size=30,
                                on_click=play_current,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )

    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}"
        print("\n=== ERROR ===")
        print(error_msg)
        print("Detailed traceback:")
        print(traceback.format_exc())
        page.add(ft.Text(error_msg, color="red", size=16, weight="bold"))
        if hasattr(page, 'db'):
            page.db.close()

if __name__ == "__main__":
    print("\n=== Starting Application ===")
    ft.app(target=main)