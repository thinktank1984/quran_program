# File: app.py
import flet as ft
from db_functions import init_db, get_current_aya, update_current_aya, load_aya_data, get_speed, update_speed
from components.page import create_page
from components.audio_player import create_audio_player, handle_audio_position_changed, play_current, next_item_and_play

class QuranApp:
    def __init__(self):
        self.current_index = 0
        self.aya_data = []
        self.sura_map = {}
        self.audio_player = None
        self.speed = None  # Will be loaded from DB in init_db()
        self.aya_duration = None
        self.play_begining_of_aya_is_true = False
        self.audio_volume = 1.0
        #init db
        # Initialize database and load data
        init_db()
        self.aya_data = load_aya_data()
        if not self.aya_data:
            raise ValueError("No aya data found in database")
        self.current_index = self.get_current_aya() - 1

        # Get unique sura names and their first ayah indices
        for item in self.aya_data:
            if item['sura_name'] not in self.sura_map:
                self.sura_map[item['sura_name']] = {
                    'first_index': self.aya_data.index(item),
                    'last_aya': max(x['aya'] for x in self.aya_data if x['sura_name'] == item['sura_name'])
                }
        #should be removed to app level
        self.audio_player = self.setup_audio_player(self.aya_data[self.current_index]['audio'])
        
        
    def audio_position_changed(self, e):
        """Handle audio position changes."""
        handle_audio_position_changed(
            self.audio_player,
            self.aya_duration,
            self.play_begining_of_aya_is_true,
            self.audio_volume
        )

    def set_play_beginning_of_aya(self, e):
        """Handle play beginning of aya button click."""
        self.play_begining_of_aya_is_true = True
        print(f"[DEBUG] Play beginning of aya flag set to: {self.play_begining_of_aya_is_true}")
        
    def setup_audio_player(self, src, should_play_on_load=False, playback_rate=None):
        """Create an audio player with the specified source and playback rate."""
        def on_state_changed(e):
            """Handle audio state changes."""
            print(f"Audio state changed: {e.data}")
            if e.data == "completed":
                # Move to next item after audio completes
                self.current_index = (self.current_index + 1) % len(self.aya_data)
                if hasattr(self, 'update_content'):
                    self.update_content()
                
        def on_loaded(e):
            """Handle audio loaded event."""
            print("Audio loaded")
            self.aya_duration = self.audio_player.get_duration()
            if should_play_on_load:
                play_current(self.audio_player)
                
        # Use stored speed if no playback_rate provided
        if playback_rate is None:
            playback_rate = self.speed
            
        self.audio_player = create_audio_player(
            initial_src=src,
            on_loaded=on_loaded,
            on_duration_changed=lambda _: None,
            on_position_changed=self.audio_position_changed,
            on_state_changed=on_state_changed,
            on_seek_complete=lambda _: None,
            playback_rate=playback_rate
        )
        return self.audio_player
        
    def next_item_and_play(self):
        """Play current item then move to next when complete."""
        next_item_and_play(self.audio_player)
            
    def play_current(self):
        """Play the current aya."""
        play_current(self.audio_player, self.audio_volume)

    def init_db(self):
        """Initialize the database."""
        init_db()
        # Load initial speed
        self.speed = get_speed()

    def update_current_aya(self, aya_id):
        """Update the current aya in the database."""
        update_current_aya(aya_id)

    def get_current_aya(self):
        """Get the current aya from the database."""
        return get_current_aya()

    def load_aya_data(self):
        """Load aya data from SQLite database."""
        self.aya_data = load_aya_data()
        return self.aya_data

    def update_speed(self, speed):
        """Update the playback speed."""
        update_speed(speed)
        self.speed = speed
        if self.audio_player:
            self.audio_player.playback_rate = speed

    def build_sura_dropdown(self):
        """Create dropdown for surah selection."""
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
        """Create dropdown for ayah selection."""
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
        """Find the index of a specific ayah in a surah."""
        for i, item in enumerate(self.aya_data):
            if item['sura_name'] == sura_name and item['aya'] == aya_number:
                return i
        return None

    def page(self, page: ft.Page):
        """Create and configure the main application page."""
        create_page(self, page)