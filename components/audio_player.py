# File: components/audio_player.py
import flet_audio as fta

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
    """Create and configure an audio player."""
    return fta.Audio(
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

def handle_audio_position_changed(player, aya_duration, play_begining_of_aya_is_true, audio_volume):
    """Handle audio position changes and volume fading."""
    if not hasattr(handle_audio_position_changed, 'last_volume_update'):
        handle_audio_position_changed.last_volume_update = 0

    if aya_duration and play_begining_of_aya_is_true:
        current_position = float(player.get_current_position())
        thirty_percent = aya_duration * 0.3
        sixty_percent = aya_duration * 0.6

        print(f"[DEBUG] Position: {current_position:.2f}/{aya_duration:.2f} (30%={thirty_percent:.2f}, 60%={sixty_percent:.2f})")

        if current_position > sixty_percent:
            player.pause()
            play_begining_of_aya_is_true = False
            audio_volume = 1.0
            player.volume = audio_volume
            player.update()
            print("[DEBUG] Stopped at 60%, reset flag to False and volume to 1.0")
        elif current_position > thirty_percent:
            if current_position - handle_audio_position_changed.last_volume_update >= 0.1:
                handle_audio_position_changed.last_volume_update = current_position

                fade_position = current_position - thirty_percent
                fade_period = sixty_percent - thirty_percent

                print(f"[DEBUG] Current volume before fade: {audio_volume:.3f}")
                fade_progress = fade_position / fade_period
                fade_factor = (1 - fade_progress) ** 2
                audio_volume = max(0.0, min(1.0, fade_factor))
                player.volume = audio_volume
                player.update()
                print(f"[DEBUG] Volume decreased to: {audio_volume:.3f}")

def play_current(player, audio_volume=1.0):
    """Play the current audio with full volume."""
    print("Playing current audio")
    if player:
        player.volume = audio_volume
        player.play()

def next_item_and_play(player):
    """Play the current audio item."""
    print("Playing current item")
    if player:
        player.play()