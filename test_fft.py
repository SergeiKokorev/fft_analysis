import os
import numpy as np
import matplotlib.pyplot as plt

from scipy.fft import fft, fftfreq, fftshift
from scipy.signal.windows import hann


from tools import *


if __name__ == "__main__":

    unit = 1

    infile = r'E:\Kokorev\fft_data\ptotin2\pdiff1.csv'
    data = get_data(infile)
    pressure = data['y']
    pressure = pressure * unit
    pressure = pressure - pressure.mean()
    n = pressure.size
    time = data['x']
    wsignal = pressure * hann(n)
    fft_data = fft(wsignal)
    density = np.array([abs(fft_data[i]) ** 2 if i == 0 else 2 * abs(fft_data[i]) ** 2 for i in range(n)])

    dt = time[1] - time[0]
    fs = 1 / dt
    freq = fftfreq(n, dt)

    fig, axs = plt.subplots(3, 1)
    axs[0].plot(time, pressure)
    axs[1].plot(time, wsignal)
    axs[2].plot(freq, density)

    plt.show()

    outfile = r'E:\Kokorev\fft_data\ptotin2\out.csv'
    with open(outfile, 'w', newline='') as f:
        for a, fr in zip(abs(fft_data), freq):
            f.write(f'{fr},{a}\n')
