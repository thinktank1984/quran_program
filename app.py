import flet as ft
import sqlite3
from components.page import create_page
from components.audio_player import create_audio_player
from db_functions import init_db, get_current_aya, update_current_aya, load_aya_data, get_speed, update_speed

class QuranApp:
    def __init__(self):
        self.current_index = 0
        self.aya_data = []
        self.sura_map = {}
        self.audio_player = None
        self.speed = None  # Will be loaded from DB in init_db()
        self.aya_duration = None
        
    def audio_position_changed(self, e):
        """Handle audio position changes"""
        print(f"Current position: {e.data}")

    def create_audio_player(self, src, should_play_on_load=False, playback_rate=None):
        """Create an audio player with the specified source and playback rate"""
        def on_state_changed(e):
            """Handle audio state changes"""
            print(f"Audio state changed: {e.data}")
            if e.data == "completed":
                # Move to next item after audio completes
                self.current_index = (self.current_index + 1) % len(self.aya_data)
                if hasattr(self, 'update_content'):
                    self.update_content()
                
        def on_loaded(e):
            """Handle audio loaded event"""
            print("Audio loaded")
            self.aya_duration = self.audio_player.get_duration()
            if should_play_on_load:
                self.play_current()
                
        # Use stored speed if no playback_rate provided
        if playback_rate is None:
            playback_rate = self.speed
            
        return create_audio_player(
            initial_src=src,
            on_loaded=on_loaded,
            on_duration_changed=lambda _: None,
            on_position_changed=self.audio_position_changed,
            on_state_changed=on_state_changed,
            on_seek_complete=lambda _: None,
            playback_rate=playback_rate
        )
        
    def next_item_and_play(self):
        """Play current item then move to next when complete"""
        print("Playing current item")
        if self.audio_player:
            self.audio_player.play()
            
    def play_current(self):
        """Play the current aya"""
        print("Playing current aya")
        if self.audio_player:
            self.audio_player.play()
        
    def init_db(self):
        """Initialize the database"""
        conn = None
        try:
            conn = sqlite3.connect('aya.db')
            init_db(conn)
            # Load initial speed
            self.speed = get_speed(conn)
        finally:
            if conn:
                conn.close()

    def update_current_aya(self, aya_id):
        """Update the current aya in the database"""
        conn = None
        try:
            conn = sqlite3.connect('aya.db')
            update_current_aya(conn, aya_id)
        finally:
            if conn:
                conn.close()

    def get_current_aya(self):
        """Get the current aya from the database"""
        conn = None
        try:
            conn = sqlite3.connect('aya.db')
            return get_current_aya(conn)
        finally:
            if conn:
                conn.close()

    def load_aya_data(self):
        """Load aya data from SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect('aya.db')
            self.aya_data = load_aya_data(conn)
            return self.aya_data
        finally:
            if conn:
                conn.close()

    def update_speed(self, speed):
        """Update the playback speed"""
        conn = None
        try:
            conn = sqlite3.connect('aya.db')
            update_speed(conn, speed)
            self.speed = speed
            if self.audio_player:
                self.audio_player.playback_rate = speed
        finally:
            if conn:
                conn.close()

    def build_sura_dropdown(self):
        """Create dropdown for surah selection"""
        return ft.Dropdown(
            width=200,
            label="Select Surah",
            value=self.aya_data[self.current_index]['sura_name'],
            options=[
                ft.dropdown.Option(text=sura_name) 
                for sura_name in sorted(self.sura_map.keys())
            ],
        )

    def build_aya_dropdown(self, sura_name):
        """Create dropdown for ayah selection"""
        max_aya = self.sura_map[sura_name]['last_aya']
        return ft.Dropdown(
            width=100,
            label="Select Ayah",
            value=str(self.aya_data[self.current_index]['aya']),
            options=[
                ft.dropdown.Option(text=str(i)) 
                for i in range(1, max_aya + 1)
            ],
        )

    def find_aya_index(self, sura_name, aya_number):
        """Find the index of a specific ayah in a surah"""
        for i, item in enumerate(self.aya_data):
            if item['sura_name'] == sura_name and item['aya'] == aya_number:
                return i
        return None

    def page(self, page: ft.Page):
        """Create and configure the main application page"""
        create_page(self, page)
