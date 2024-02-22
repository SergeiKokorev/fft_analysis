import numpy as np

from abc import ABCMeta
from scipy.fft import fft, fftfreq


from models.data import Signal


class Analysis(metaclass=ABCMeta):

    def __init__(self):
        self.__model: Signal = None

    def set_model(self, model: Signal):
        if not isinstance(model, Signal):
            raise TypeError('Unsupported type fo signal processing')
        self.__model = model
    
    def get_model(self):
        return self.__model


class Regression(Analysis):

    def __init__(self):
        super().__init__()


class FFT(Analysis):

    def __init__(self):
        super().__init__()

    def get_frequency(self, sides: int = 1):
        if sides not in [1, 2]:
            raise TypeError('Unsupported sides type for Frequency')
        freq = fftfreq(self.__model.N, self.__model.dt)
        if (self.__model.N % sides == 0 or sides == 1):
            n = int(self.__model.N / sides)
        else:
            n = self.__model.N // sides + 1
        return freq[:n]

    def get_fft(self):
        return fft(self.__model.y)
    
    def get_spectral_density(self):
        return np.array([abs(phi) ** 2 if i == 0 else 2 * abs(phi) ** 2 for i, phi in enumerate(self.get_fft())])
    
    def get_amplitude(self):
        return self.get_spectral_density() ** 0.5
    
    def get_sound_pressure_level(self, pref: float=2e-5):
        return 10 * np.log((self.get_spectral_density() ** 2) / (pref ** 2))
    
    def get_sound_amplitude(self, pref: float=2e-5):
        return 10 * np.log((self.get_spectral_density() ** 2) / (pref ** 2) ** 0.5)
