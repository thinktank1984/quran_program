# File: components/image_display.py
import flet as ft

def create_image_display(initial_src, width=400, height=400):
    image = ft.Image(
        src=initial_src,
        width=width,
        height=height,
        fit=ft.ImageFit.CONTAIN,
    )
    
    def update_source(new_src):
        image.src = new_src
        image.update()
    
    image.update_source = update_source
    return image
