import flet_audio as fta

class MainAudioPlayer(fta.Audio):
    def __init__(
        self,
        initial_src,
        on_loaded,
        on_duration_changed,
        on_position_changed,
        on_state_changed,
        on_seek_complete,
        volume=1.0,
        balance=0,
        playback_rate=1.0
    ):
        """Initialize and configure an audio player."""
        super().__init__(
            src=initial_src,
            autoplay=False,
            volume=volume,
            balance=balance,
            on_loaded=on_loaded,
            on_duration_changed=on_duration_changed,
            on_position_changed=on_position_changed,
            on_state_changed=on_state_changed,
            on_seek_complete=on_seek_complete,
            playback_rate=playback_rate,
        )
        self.last_volume_update = 0

    def handle_audio_position_changed(self, aya_duration, play_begining_of_aya_is_true, audio_volume):
        """Handle audio position changes and volume fading."""
        if aya_duration and play_begining_of_aya_is_true:
            current_position = float(self.get_current_position())
            thirty_percent = aya_duration * 0.3
            sixty_percent = aya_duration * 0.6

            print(f"[DEBUG] Position: {current_position:.2f}/{aya_duration:.2f} (30%={thirty_percent:.2f}, 60%={sixty_percent:.2f})")

            if current_position > sixty_percent:
                self.pause()
                play_begining_of_aya_is_true = False
                audio_volume = 1.0
                self.volume = audio_volume
                self.update()
                print("[DEBUG] Stopped at 60%, reset flag to False and volume to 1.0")
            elif current_position > thirty_percent:
                if current_position - self.last_volume_update >= 0.1:
                    self.last_volume_update = current_position

                    fade_position = current_position - thirty_percent
                    fade_period = sixty_percent - thirty_percent

                    print(f"[DEBUG] Current volume before fade: {audio_volume:.3f}")
                    fade_progress = fade_position / fade_period
                    fade_factor = (1 - fade_progress) ** 2
                    audio_volume = max(0.0, min(1.0, fade_factor))
                    self.volume = audio_volume
                    self.update()
                    print(f"[DEBUG] Volume decreased to: {audio_volume:.3f}")

    def play_current(self, audio_volume=1.0):
        """Play the current audio with passed volume."""
        print("Playing current audio")
        if self:
            self.volume = audio_volume
            self.play()
            
def create_audio_player(
    initial_src,
    on_loaded,
    on_duration_changed,
    on_position_changed,
    on_state_changed,
    on_seek_complete,
    volume=1.0,
    balance=0,
    playback_rate=1.0
):
    """Factory function to create and return a MainAudioPlayer instance."""
    return MainAudioPlayer(
        initial_src=initial_src,
        on_loaded=on_loaded,
        on_duration_changed=on_duration_changed,
        on_position_changed=on_position_changed,
        on_state_changed=on_state_changed,
        on_seek_complete=on_seek_complete,
        volume=volume,
        balance=balance,
        playback_rate=playback_rate
    )
    
# Example usage:
# player = MainAudioPlayer(
#     initial_src="path/to/audio.mp3",
#     on_loaded=lambda e: print("Loaded"),
#     on_duration_changed=lambda e: print("Duration Changed"),
#     on_position_changed=lambda e: print("Position Changed"),
#     on_state_changed=lambda e: print("State Changed"),
#     on_seek_complete=lambda e: print("Seek Complete"),
#     volume=1.0,
#     balance=0,
#     playback_rate=1.0
# )
# player.play_current()