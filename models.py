import numpy as np

from scipy.fft import fft, fftfreq


from typing import Sequence, Tuple
from abc import ABCMeta, abstractmethod, abstractproperty


from windows import WINDOWS as window


class Signal(metaclass=ABCMeta):
    
    def __init__(self, x, y, *, file, xlabel, ylabel, name, xlimits) -> None:
        self._x: Sequence = np.array(x)
        self._y: Sequence = np.array(y)
        self._xlabel: str = xlabel
        self._ylabel: str = ylabel
        self._name: str = name
        self._xlimits: Tuple = xlimits
        self._file: str = file

    def __min__(self):
        try:
            return np.where(self._xlimits[0] >= self._x)[0][-1]
        except IndexError:
            return 0
        
    def __max__(self):
        try:
            return np.where(self._xlimits[1] <= self._x)[0][0]
        except IndexError:
            return self._x.size - 1

    @property
    def x(self):
        imin, imax = self.__min__(), self.__max__()
        return self._x[imin:imax]
    
    @property
    def y(self):
        imin, imax = self.__min__(), self.__max__()
        return self._y[imin:imax]
    
    @property
    def xlabel(self):
        return self._xlabel
    
    @property
    def ylabel(self):
        return self._ylabel
    
    @property
    def name(self):
        return self._name
    
    @property
    def xlimits(self):
        return self._xlimits

    @property
    def file(self):
        return self._file

    @abstractproperty
    def info(self) -> str:
        pass

    @xlabel.setter
    def xlabel(self, lb: str):
        if not isinstance(lb, str): raise TypeError('Unsupported type for xlabel')
        self._xlabel = lb

    @ylabel.setter
    def ylabel(self, lb: str):
        if not isinstance(lb, str): raise TypeError('Unsupported type for ylabel')
        self._ylabel = lb

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str): raise TypeError('Unsupported type for name')
        self._xlabel = name

    @xlimits.setter
    def xlimits(self, limits: Tuple):
        if not hasattr(limits, '__iter__'):
            raise TypeError('X limits must be tuple or list type')
        if not all([isinstance(i, float | complex | int) for i in limits]):
            raise ValueError('X Limits must be float, int or complex type')
        self._xlimits = limits

    @abstractmethod
    def crop(self, xmin, xmax) -> Sequence:
        pass

    @abstractmethod
    def update(self, **data) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class SignalCash(metaclass=ABCMeta):

    def __init__(self) -> None:
        pass

    @abstractproperty
    def signals(self):
        pass
    
    @abstractmethod
    def add(self, signal: Signal) -> bool:
        pass

    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass

    @abstractmethod
    def insert(self, idx: int, signal: Signal) -> bool:
        pass
    
    @abstractmethod
    def get(self, idx: int) -> Signal:
        pass

    def __str__(self):
        return str([str(s) + '\n' for s in self.__cash])[1:-1]


class Input(Signal):
    
    def __init__(self, x, y, *, file, xlabel='X', ylabel='Y', name='Plot', xlimits=None) -> None:
        super().__init__(x, y, file=file, xlabel=xlabel, ylabel=ylabel, name=name, xlimits=xlimits)
        if not self.xlimits:
            self._xlimits = (self._x[0], self._x[-1])

    @property
    def dt(self):
        return self.x[1] - self.x[0]

    @property
    def N(self):
        return self.x.size

    @property
    def info(self) -> str:
        return f'Input Signal Name: {self.name}\n\tInput file: {self.file}\n' \
        f'\t{self._xlabel}: step = {self.dt} Interval: {self.x[0]} ... {self.x[-1]}\n' \
        f'\tInterval boundaries: xmin = {self._xlimits[0]}, xmax = {self._xlimits[1]}\n'

    def crop(self, xmin, xmax):
        imin, imax = np.where(xmin >= self._x)[0][-1], np.where(xmax <= self._x)[0][0]
        self.xlimits = (self._x[imin], self._x[imax])
        return (imin, imax)

    @classmethod
    def get_frequency(cls, n, dt):
        fs = 1 / dt
        return np.array([j * fs / n for j in range(n)])
    
    @classmethod
    def get_spectral_density(cls, signal):
        return np.array([abs(phi) ** 2 if i == 0 else 2 * abs(phi) ** 2 for i, phi in enumerate(cls.get_fft(signal))])

    @classmethod
    def get_amplitude(cls, signal):
        density = cls.get_spectral_density(signal)
        return density ** 0.5
    
    @classmethod
    def get_sound_pressure_level(cls, signal, pref: float = 2e-5):
        density = cls.get_spectral_density(signal)
        return 10 * np.log((density ** 2) / (pref ** 2))

    @classmethod
    def get_sound_amplitude(cls, signal, pref: float = 2e-5):
        density = cls.get_spectral_density(signal)
        return 10 * np.log(((density ** 2) / (pref ** 2)) ** 0.5)

    @classmethod
    def get_fft(cls, signal):
        return fft(signal)

    @classmethod
    def window(cls, signal, w: str) -> Sequence:
        n = signal.size
        return signal * window[w](n)

    @classmethod
    def subtrackt_mean(cls, signal):
        return signal - signal.mean()

    def update(self, *, xlabel=None, ylabel=None, xlimits=None) -> None:
        if xlabel:
            self._xlabel = xlabel
        if ylabel:
            self._ylabel = ylabel
        if xlimits:
            self._xlimits = xlimits
        
    def reset(self):
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self._name = 'Plot'
        self.xlimits = (self._x[0], self._x[-1])
        
    def __str__(self):
        return self._name


# class Output(Signal):

#     def __init__(self, x, y, input, file=None, xlabel='Frequency [Hz]', ylabel='Amplitude', name='FTT', xlimits=None,) -> None:
#         super(Output, self).__init__(x, y, file=file, xlabel=xlabel, ylabel=ylabel, name=name, xlimits=xlimits)
#         self._input: Input = input
#         self._y = fft(self._input.x)
#         self._x = fftfreq(self._input.x.size, self._input.x[1] - self._input.x[0])
#         print(self._x)
#         n = self._x.size
#         self._x = self._x[int(n / 2):]
#         print(self._x)
#         self._y = self._y[int(n / n):]
#         if not self.xlimits:
#             self._xlimits = (self._x[0], self._x[-1])

#     @property
#     def info(self):
#         return f'Output Signal Name: {self.name}\n' \
#             f'\t{self._xlabel}: beam = {self.beam} Interval: {self.x[0]} ... {self.x[-1]}\n' \
#             f'Interval boundaries: xmin = {self._xlimits[0]}, xmax = {self._xlimits[1]}\n'

#     @property
#     def frequency(self):
#         return self._y
    
#     @property
#     def beam(self):
#         return self._x[1] - self._x[0]

#     @property
#     def amplitude(self):
#         return abs(self._y)

#     @property
#     def density(self):
#         return np.array([a ** 2 if i == 0 else 2 * a ** 2 for i, a in enumerate(abs(self._y))])
    
#     def crop(self, fmin, fmax) -> Tuple:
#         imin, imax = np.where(fmin >= self._x), np.where(fmax <= self._x)
#         self.xlimits = (self._x[imin], self._x[imax])
#         return (imin, imax)
    
#     def reset(self) -> None:
#         self.xlabel = 'Frequency [Hz]'
#         self.ylabel = f'Amplitude {self._input.ylabel}'
#         self._name = f'FFT {self._input.name}'
#         self.xlimits = (self._x[0], self._x[-1])

#     def update(self, *, x=None, xlabel=None, ylabel=None, name=None, xlimits=None):
#         if x:
#             self._x = fft(x)
#             self._y = fftfreq(self.x.size, self.x[1] - self.x[0])
#         if xlabel:
#             self.xlabel = xlabel
#         if ylabel:
#             self.ylabel = ylabel
#         if name:
#             self.name = name
#         if xlimits:
#             self.xlimits = xlimits

#     def __str__(self):
#         return self._name


class InputSignals(SignalCash):

    def __init__(self) -> None:
        super(InputSignals, self).__init__()
        self.__cash = []

    @property
    def signals(self):
        return self.__cash

    def add(self, signal: Input) -> bool:
        if not isinstance(signal, Input): return False
        self.__cash.append(signal)
        return True

    def delete(self, idx: int) -> bool:
        if not isinstance(idx, int): return False
        try:
            self.__cash.pop(idx)
            return True
        except IndexError:
            return False
        
    def insert(self, idx: int, signal: Input) -> bool:
        if not isinstance(idx, int): return False
        if not isinstance(signal, Input): return False
        try:
            self.__cash.insert(idx, signal)
        except IndexError:
            return False
        
    def get(self, idx: int) -> Input:
        try:
            return self.__cash[idx]
        except IndexError:
            return False


# class OutputSignals(SignalCash):

#     def __init__(self) -> None:
#         super(OutputSignals, self).__init__()
#         self.__cash = []

#     @property
#     def signals(self):
#         return self.__cash
    
#     def add(self, signal: Output) -> bool:
#         if not isinstance(signal, Output): return False
#         self.__cash.append(signal)
#         return True

#     def delete(self, idx: int) -> bool:
#         if not isinstance(idx, int): return False
#         try:
#             self.__cash.pop(idx)
#             return True
#         except IndexError:
#             return False
        
#     def insert(self, idx: int, signal: Output) -> bool:
#         if not isinstance(idx, int): return False
#         if not isinstance(signal, Output): return False
#         try:
#             self.__cash.insert(idx, signal)
#         except IndexError:
#             return False
        
#     def get(self, idx: int) -> Tuple[Output, int]:
#         try:
#             return self.__cash[idx]
#         except IndexError:
#             return False
