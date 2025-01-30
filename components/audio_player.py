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
