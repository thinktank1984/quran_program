# File: components/status_bar.py
import flet as ft

def create_status_bar(initial_sura, initial_aya, initial_suffix=""):
    text = f"Surah {initial_sura} - Ayah {initial_aya}"
    if initial_suffix:
        text += f" - {initial_suffix}"
    
    status_text = ft.Text(
        text,
        size=16,
        weight="bold"
    )
    
    def update_status(sura, aya, suffix=""):
        text = f"Surah {sura} - Ayah {aya}"
        if suffix:
            text += f" - {suffix}"
        status_text.value = text
        status_text.update()
    
    status_text.update_status = update_status
    return status_text
