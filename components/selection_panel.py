# File: components/selection_panel.py
import flet as ft

def build_selection_panel(sura_data, initial_sura, initial_aya, on_sura_change, on_aya_change):
    panel = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    sura_dropdown = ft.Dropdown(
        width=200,
        label="Select Surah",
        value=initial_sura,
        options=[
            ft.dropdown.Option(text=sura_name)
            for sura_name in sorted(sura_data.keys())
        ],
        on_change=on_sura_change
    )

    aya_dropdown = ft.Dropdown(
        width=100,
        label="Select Ayah",
        value=str(initial_aya),
        options=[
            ft.dropdown.Option(text=str(i))
            for i in range(1, sura_data[initial_sura]['last_aya'] + 1)
        ],
        on_change=on_aya_change
    )
    
    panel.controls = [sura_dropdown, aya_dropdown]
    
    def update_aya_options(sura_name):
        aya_dropdown.options = [
            ft.dropdown.Option(text=str(i))
            for i in range(1, sura_data[sura_name]['last_aya'] + 1)
        ]
        aya_dropdown.value = "1"
        aya_dropdown.update()
    
    # Add components as attributes
    panel.sura_dropdown = sura_dropdown
    panel.aya_dropdown = aya_dropdown
    panel.update_aya_options = update_aya_options
    
    return panel
