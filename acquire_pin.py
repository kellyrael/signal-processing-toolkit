import numpy as np
from compute_fft import compute_fft
from find_average_frequency import average_frequency
import matplotlib.pyplot as plt

def acquire_pin(pin_number, sampling_period):
    """
    Plot a 1-D array of doubles against time derived from the sampling period.

    Parameters
    ----------
    pin_number : int
        Time between consecutive samples, in seconds.
    sampling_period : float
        Time between consecutive samples, in seconds.

    Returns
    -------
    sig : np.ndarray
    """
    t = np.arange(0, 1, sampling_period)

    if pin_number == 1:
        sig = 3 * np.sin(2 * np.pi * 50 * t) + 1.5 * np.sin(2 * np.pi * 120 * t)

    elif pin_number == 2:
        sig = 3 * np.sin(5 * np.pi * 100 * t)
    else :
        sig = 3 * np.sin(6 * np.pi * 200 * t)

    return sig