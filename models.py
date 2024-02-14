import numpy as np

from scipy.fft import fft, fftfreq, fftshift


from typing import Sequence, Tuple
from dataclasses import dataclass
from const import WINDOWS




@dataclass
class Signal:
    input: Sequence[Tuple]
    file: str
    name: str
    xlabel: str = 'x'
    ylabel: str = 'f(x)'

    def __post_init__(self):
        self.input = np.array(self.input)

    @property
    def dt(self):
        return self.input[1, 0] - self.input[0, 0]

    @property
    def fs(self):
        return 1 / self.dt

    @property
    def output(self):
        return fft(self.input[:,1])

    @property
    def frequency(self):
        n = self.input.shape[0]
        return fftfreq(n, self.dt)

    @property
    def amplitude(self):
        return abs(self.output)

    @property
    def density(self):
        n = self.input.hape[0]
        return np.array([self.amplitude[i] ** 2 if i == 0 else 2 * self.amplitude[i] ** 2 for i in range(n)])

    def update(self, **data):

        if (name := data.get('name', None)):
            self.name = name

        if (xlabel := data.get('xlabel', None)):
            self.xlabel = xlabel

        if (ylabel := data.get('ylabel', None)):
            self.ylabel = ylabel

        if (input := data.get('input', None)):
            self.input = np.array(input)

        if (window := data.get('window', None)):
            n = self.input.shape[0]
            w = WINDOWS[window](n)
            self.input = np.array([(self.input[i][0], self.input[i][1] * w[i]) for i in range(n)])

    def info(self) -> str:
        n = len(self.input)
        string = f'Input file {self.file}\n'
        string = f'Signal name {self.name}\n'
        string += f'\tNumber of discret signals N = {n}\n'
        string += f'\tTime Domain:\n\t\tdelta time = {self.dt};\n'
        string += f'\t\tt0 = {self.input[0,0]};\n'
        string += f'\t\tt{n} = {self.input[1,0]}\n'
        return string

    def __str__(self):
        return self.name


class SignalCash:
    signals = []

    def add(self, signal: Signal):

        if not isinstance(signal, Signal):
            raise TypeError('Unsupported variable type for signal')
        
        self.signals.append(signal)

    def get(self, idx: int) -> Signal:
        return self.signals[idx]

    def delete(self, index: int):
        self.signals.pop(index)

    def data(self):
        return self.signals
    
    def view(self):
        return [str(signal) for signal in self.signals]
