#components\page.py
import flet as ft
import traceback
from pynput import keyboard

def create_page(app, page: ft.Page):
    """Create and configure the main application page"""
    
    # Setup keyboard listener
    def on_key_press(key):
        try:
            if key == keyboard.Key.right:
                app.next_item_and_play()
            elif key == keyboard.Key.left:
                prev_item()
        except Exception as e:
            print(f"Error processing key event: {e}")
    
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()
    print("\n=== Starting Quran Audio Image App ===")
    page.title = "Quran Audio Image App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.theme_mode = "light"
    page.keyboard_shortcuts = False  # Disable default keyboard navigation
    
    # Prevent focus changes
    def on_keyboard_event(e: ft.KeyboardEvent):
        e.prevent_default = True
    page.on_keyboard_event = on_keyboard_event

    try:
        

        status_text = ft.Text(
            f"Surah {app.aya_data[app.current_index]['sura_name']} - Ayah {app.aya_data[app.current_index]['aya']}", 
            size=16,
            weight="bold"
        )

        speed_text = ft.Text(f"Speed: {app.speed}x", size=14)

        def update_speed(change):
            current_rate = app.speed
            new_rate = round(current_rate + change, 1)
            # Ensure speed stays within reasonable bounds
            new_rate = max(0.5, min(2.0, new_rate))
            app.update_speed(new_rate)
            speed_text.value = f"Speed: {new_rate}x"
            page.update()

        # Create dropdowns
        sura_dropdown = app.build_sura_dropdown()
        aya_dropdown = app.build_aya_dropdown(app.aya_data[app.current_index]['sura_name'])

        page.overlay.append(app.audio_player)

        img_display = ft.Image(
            src=app.aya_data[app.current_index]['image'],
            width=None,
            height=300,
            fit=ft.ImageFit.CONTAIN,
        )

        def update_content():
            """Update the UI content"""
            print(f"\n=== Updating content for index {app.current_index} ===")
            speed_text.value = f"Speed: {app.speed}x"

            # Update image and text
            img_display.src = app.aya_data[app.current_index]['image']
            suffix = app.aya_data[app.current_index]['aya_suffix']
            suffix_display = f" - {suffix}" if suffix else ""
            status_text.value = f"Surah {app.aya_data[app.current_index]['sura_name']} - Ayah {app.aya_data[app.current_index]['aya']}{suffix_display}"

            # Update dropdown selections
            sura_dropdown.value = app.aya_data[app.current_index]['sura_name']
            aya_dropdown.value = str(app.aya_data[app.current_index]['aya'])

            # Update database
            app.update_current_aya(app.aya_data[app.current_index]['id'])

            # Dispose of the old audio player if it exists
            if hasattr(app, 'audio_player') and app.audio_player:
                page.overlay.remove(app.audio_player)
                app.audio_player._dispose()
                #page.update()

            # Create and configure the new audio player
            app.audio_player = app.setup_audio_player(app.aya_data[app.current_index]['audio'])
            app.audio_player.playback_rate = app.speed
            page.overlay.append(app.audio_player)

            # Update the page and audio player
            page.update()
            app.audio_player.update()
            print("Content update complete")

        def on_sura_change(e):
            """Handle surah selection change"""
            selected_sura = sura_dropdown.value
            # Update ayah dropdown with new range
            aya_dropdown.options = [
                ft.dropdown.Option(text=str(i)) 
                for i in range(1, app.sura_map[selected_sura]['last_aya'] + 1)
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

            new_index = app.find_aya_index(sura_dropdown.value, int(aya_dropdown.value))
            if new_index is not None:
                app.current_index = new_index
                update_content()

        def prev_item(e=None):
            """Move to previous item without playing"""
            app.current_index = (app.current_index - 1) % len(app.aya_data)
            print(f"Moving to previous item, new index: {app.current_index}")
            update_content()

        # Store update_content method on app instance for use in callbacks
        app.update_content = update_content
        
        sura_dropdown.on_change = on_sura_change
        aya_dropdown.on_change = on_aya_change

       # Add elements to page using ResponsiveRow
        page.add(
            ft.ResponsiveRow(
                [
                    ft.Column(
                        [status_text],
                        col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [ft.Row(
                            [sura_dropdown, aya_dropdown],
                            alignment=ft.MainAxisAlignment.CENTER,
                        )],
                        col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [img_display],
                        col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.SKIP_PREVIOUS,
                                        icon_size=24,
                                        on_click=prev_item,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.PLAY_ARROW,
                                        icon_size=24,
                                        on_click=lambda e: app.audio_player.play_current(speed=app.speed),
                                    ),
                                    ft.Switch(label="Play beginning of aya", value=False, on_change=lambda e: app.toggle_play_beginning_of_aya(e))
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.REMOVE,
                                        icon_size=20,
                                        on_click=lambda e: update_speed(-0.1),
                                        tooltip="Decrease speed",
                                    ),
                                    speed_text,
                                    ft.IconButton(
                                        icon=ft.icons.ADD,
                                        icon_size=20,
                                        on_click=lambda e: update_speed(0.1),
                                        tooltip="Increase speed",
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            )
        )

    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}"
        print("\n=== ERROR ===")
        print(error_msg)
        print("Detailed traceback:")
        print(traceback.format_exc())
        page.add(ft.Text(error_msg, color="red", size=16, weight="bold"))
