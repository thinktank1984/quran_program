import flet
from flet import IconButton, Page, Row, TextField, icons, Column, Image, Audio, Text, ProgressRing
import csv
import os
from pathlib import Path

def main(page: Page):
    page.title = "Quran Audio Image App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.theme_mode = "light"

    # Create q_files if it doesn't exist
    os.makedirs('q_files', exist_ok=True)

    try:
        # Load CSV file
        audio_files = []
        csv_path = 'quran_download.csv'

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                audio_path = os.path.join('q_files', row['audio'])
                image_path = os.path.join('q_files', row['image'])
                
                if not os.path.exists(audio_path):
                    print(f"Warning: Audio file missing: {audio_path}")
                    continue
                    
                if not os.path.exists(image_path):
                    print(f"Warning: Image file missing: {image_path}")
                    continue
                
                audio_files.append({
                    'audio': audio_path,
                    'image': image_path
                })

        if not audio_files:
            raise ValueError("No valid audio/image pairs found. Please check q_files folder.")

        current_index = 0

        # Status text with total count
        status_text = Text(
            f"Ayah {current_index + 1} of {len(audio_files)}", 
            size=16,
            weight="bold"
        )

        # Initialize audio player
        audio_player = Audio(
            src=audio_files[current_index]['audio'],
            autoplay=False,
            volume=1.0
        )
        page.overlay.append(audio_player)

        # Initialize image display
        img_display = Image(
            src=audio_files[current_index]['image'],
            fit=flet.ImageFit.CONTAIN,
            width=400,
            height=400,
            border_radius=10
        )

        def play_audio(e):
            audio_player.play()

        def pause_audio(e):
            audio_player.pause()

        def next_item(e):
            nonlocal current_index
            current_index = (current_index + 1) % len(audio_files)
            update_content()

        def prev_item(e):
            nonlocal current_index
            current_index = (current_index - 1) % len(audio_files)
            update_content()

        def update_content():
            audio_player.src = audio_files[current_index]['audio']
            img_display.src = audio_files[current_index]['image']
            status_text.value = f"Ayah {current_index + 1} of {len(audio_files)}"
            page.update()

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
        print(error_msg)  # Print to console
        page.add(Text(error_msg, color="red", size=16, weight="bold"))

if __name__ == "__main__":
    flet.app(target=main)