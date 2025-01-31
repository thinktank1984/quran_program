import flet as ft
from pynput import keyboard
import platform
import time

class KeyboardInputHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Bluetooth Ring Input Handler"
        self.raw_events = []
        self.setup_ui()
        self.setup_keyboard_listener()

    def setup_ui(self):
        # Raw HID event display
        self.raw_event_text = ft.TextField(
            label="Raw HID Events",
            multiline=True,
            read_only=True,
            min_lines=10,
            max_lines=10,
            text_size=14,
            value="Waiting for HID events...\n",
            border_color=ft.colors.BLUE_400
        )

        # Input event display
        self.event_text = ft.Text("Waiting for input...", size=16)
        self.event_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=200
        )
        
        # Clear buttons
        self.clear_history_btn = ft.ElevatedButton(
            "Clear History",
            on_click=self.clear_history
        )
        
        self.clear_raw_btn = ft.ElevatedButton(
            "Clear Raw Events",
            on_click=self.clear_raw_events
        )

        # Button row
        button_row = ft.Row([
            self.clear_history_btn,
            self.clear_raw_btn
        ])

        # Main layout
        self.page.add(
            ft.Column([
                ft.Text("Ring Controller Input Monitor", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.raw_event_text,
                    border=ft.border.all(1, ft.colors.BLUE_200),
                    border_radius=10,
                    padding=10
                ),
                self.event_text,
                ft.Container(
                    content=self.event_list,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10
                ),
                button_row
            ])
        )

    def setup_keyboard_listener(self):
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

    def on_key_press(self, key):
        try:
            # Get timestamp
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            
            # Get detailed key information
            key_str = str(key)
            vk = getattr(key, 'vk', None)
            scan_code = getattr(key, 'scan_code', None)
            
            # Create detailed event string
            event_details = (
                f"[{timestamp}] PRESS: "
                f"Key: {key_str}, "
                f"Virtual Key: {vk}, "
                f"Scan Code: {scan_code}\n"
            )
            
            # Update raw events text field
            current_text = self.raw_event_text.value
            self.raw_event_text.value = event_details + current_text
            
            # Common mappings for media keys
            key_mappings = {
                'Key.media_play_pause': 'Play/Pause',
                'Key.media_next': 'Next',
                'Key.media_previous': 'Previous',
                'Key.page_up': 'Page Up',
                'Key.page_down': 'Page Down',
                'Key.volume_up': 'Volume Up',
                'Key.volume_down': 'Volume Down'
            }
            
            # Get friendly name if available
            event_name = key_mappings.get(key_str, key_str)
            
            # Add event to list
            self.event_list.controls.insert(
                0,
                ft.Text(f"[{timestamp}] Pressed: {event_name}")
            )
            
            # Update the current event text
            self.event_text.value = f"Last Input: {event_name}"
            
            # Keep only last 10 events in the list
            if len(self.event_list.controls) > 10:
                self.event_list.controls.pop()
            
            # Update the UI
            self.page.update()
            
        except Exception as e:
            print(f"Error processing key event: {e}")

    def on_key_release(self, key):
        try:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            key_str = str(key)
            vk = getattr(key, 'vk', None)
            scan_code = getattr(key, 'scan_code', None)
            
            event_details = (
                f"[{timestamp}] RELEASE: "
                f"Key: {key_str}, "
                f"Virtual Key: {vk}, "
                f"Scan Code: {scan_code}\n"
            )
            
            current_text = self.raw_event_text.value
            self.raw_event_text.value = event_details + current_text
            self.page.update()
            
        except Exception as e:
            print(f"Error processing key release event: {e}")

    def clear_history(self, e):
        self.event_list.controls.clear()
        self.event_text.value = "Waiting for input..."
        self.page.update()

    def clear_raw_events(self, e):
        self.raw_event_text.value = "Waiting for HID events...\n"
        self.page.update()

async def main(page: ft.Page):
    app = KeyboardInputHandler(page)

# Run the application
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)