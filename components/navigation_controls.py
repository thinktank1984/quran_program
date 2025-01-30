# File: components/navigation_controls.py
import flet as ft

def build_navigation_controls(on_previous, on_play, on_next):
    return ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.SKIP_PREVIOUS,
                icon_size=30,
                on_click=on_previous,
            ),
            ft.IconButton(
                icon=ft.icons.PLAY_ARROW,
                icon_size=30,
                on_click=on_play,
            ),
            ft.IconButton(
                icon=ft.icons.SKIP_NEXT,
                icon_size=30,
                on_click=on_next,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )