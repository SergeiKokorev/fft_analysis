import numpy as np

from scipy.fft import fft, fftfreq


from typing import Sequence, Tuple
from abc import ABCMeta, abstractmethod, abstractproperty


from windows import WINDOWS as windows


class Signal(metaclass=ABCMeta):
    
    def __init__(self, x, y, *, file, xlabel, ylabel, name, xlim, window=None, sub_mean=False) -> None:
        self._x: Sequence = np.array(x)
        self._y: Sequence = np.array(y)
        self._xlabel: str = xlabel
        self._ylabel: str = ylabel
        self._name: str = name
        self._xlim: Tuple = xlim
        self._file: str = file
        self._window: str = window
        self._sub_mean: bool = False

    def __min__(self):
        try:
            return np.where(self._xlim[0] >= self._x)[0][-1]
        except IndexError:
            return 0
        
    def __max__(self):
        try:
            return np.where(self._xlim[1] <= self._x)[0][0]
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
    def xlim(self):
        return self._xlim

    @property
    def file(self):
        return self._file

    @property
    def window(self):
        return self._window

    @property
    def sub_mean(self) -> bool:
        return self._sub_mean

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

    @xlim.setter
    def xlim(self, limits: Tuple):
        if not hasattr(limits, '__iter__'):
            raise TypeError('X limits must be tuple or list type')
        if not all([isinstance(i, float | complex | int) for i in limits]):
            raise ValueError('X Limits must be float, int or complex type')
        self._xlim = limits

    @sub_mean.setter
    def sub_mean(self, subtrackt: bool):
        if not isinstance(subtrackt, bool):
            raise TypeError('Unsupported type for subtrackt mean. Supported type \'bool\'')
        self._sub_mean = subtrackt

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
    
    def __init__(self, x, y, *, file, xlabel='X', ylabel='Y', name='Plot', xlim=None, window=None) -> None:
        super().__init__(x, y, file=file, xlabel=xlabel, ylabel=ylabel, name=name, xlim=xlim, window=window)
        if not self.xlim:
            self._xlim = (self._x[0], self._x[-1])

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
        f'\tInterval boundaries: xmin = {self._xlim[0]}, xmax = {self._xlim[1]}\n' \
        f'\twindow function {self._window}'

    def crop(self, xmin, xmax):
        imin, imax = np.where(xmin >= self._x)[0][-1], np.where(xmax <= self._x)[0][0]
        self.xlim = (self._x[imin], self._x[imax])
        return (imin, imax)

    @classmethod
    def get_frequency(cls, n, dt):
        fs = 1 / dt
        return np.array([j * fs / n for j in range(int(n / 2))])
    
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
    def window_signal(cls, signal, w: str) -> Sequence:
        n = signal.size
        return signal * windows[w](n)

    @classmethod
    def subtrackt_mean(cls, signal):
        return signal - signal.mean()

    def update(self, *, xlabel=None, ylabel=None, xlim=None, window=None, sub_mean=None) -> None:
        if xlabel:
            self._xlabel = xlabel
        if ylabel:
            self._ylabel = ylabel
        if xlim:
            self._xlim = xlim
        if window and window in windows.keys():
            self._window = window
        else:
            self._window = None
        if sub_mean:
            self.sub_mean = sub_mean
        
    def reset(self):
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self._name = 'Plot'
        self.xlim = (self._x[0], self._x[-1])
        
    def __str__(self):
        return self._name


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
        
    def reset(self):
        self.__cash.clear()

    def get(self, idx: int) -> Input:
        try:
            return self.__cash[idx]
        except IndexError:
            return False
