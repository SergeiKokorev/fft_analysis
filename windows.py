from scipy.signal.windows import hann, hamming, bartlett, blackman


WINDOWS = {
    'Hanning': hann,
    'Hamming': hamming,
    'Bartlett': bartlett,
    'Blackman': blackman
}
