import flet as ft
from app import QuranApp

def main():
    print("\n=== Starting Application ===")
    app = QuranApp()
    ft.app(target=app.page)

if __name__ == "__main__":
    main()
