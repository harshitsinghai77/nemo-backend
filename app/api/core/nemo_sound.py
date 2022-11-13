from app.api.crud.nemodeta import NemoSoundDrive

all_sounds = [
    "rain",
    "thunderstorm",
    "wind",
    "forest",
    "leaves",
    "waterstream",
    "seaside",
    "water",
    "fire",
    "coffee",
    "summernight",
    "train",
    "fan",
    "whitenoise",
    "pinknoise",
    "brownnoise",
]


def fetch_nemo_sound(sound_id: str):
    if sound_id not in all_sounds:
        return {
            "message": "Invalid sound_id: {}. Should be one of {}".format(
                sound_id, all_sounds
            )
        }

    return NemoSoundDrive.get_file_from_drive(sound_id)
