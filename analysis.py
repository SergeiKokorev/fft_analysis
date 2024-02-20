from models import Input


SPECTRAL_ANALYSIS = {
    'Amplitude': Input.get_amplitude,
    'Spectral Power Density': Input.get_spectral_density
}

SOUND_ANALYSIS = {
    'Sound Pressure Level': Input.get_sound_pressure_level,
    'Sound Amplitude': Input.get_sound_amplitude
}
