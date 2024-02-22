from scipy.signal.windows import hann, hamming, bartlett, blackman
from PySide6.QtCore import QSize


TMP = '.tmp'
SIZE = QSize(128, 24)


WINDOWS = {
    'Hanning': hann,
    'Hamming': hamming,
    'Bartlett': bartlett,
    'Blackman': blackman
}


from models.data import Input


SPECTRAL_ANALYSIS = {
    'Amplitude': Input.get_amplitude,
    'Spectral Power Density': Input.get_spectral_density
}


SOUND_ANALYSIS = {
    'Sound Pressure Level': Input.get_sound_pressure_level,
    'Sound Amplitude': Input.get_sound_amplitude
}