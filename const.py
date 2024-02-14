from scipy.signal.windows import hann, hamming, bartlett, blackman


WINDOWS = {
    'hann': hann,
    'hamming': hamming,
    'bartlett': bartlett,
    'blackman': blackman
}