import numpy as np


def compute_fft(samples, sampling_period):
    """
    Compute the FFT of a real-valued signal.

    Parameters
    ----------
    samples : array_like
        1-D array of doubles (the time-domain signal).
    sampling_period : float
        Time between consecutive samples, in seconds.

    Returns
    -------
    freqs : np.ndarray
        Frequency bins in Hz (0 .. Nyquist).
    spectrum : np.ndarray
        Complex FFT coefficients, scaled so that magnitude
        corresponds to the amplitude of each sinusoid.
    """
    x = np.asarray(samples, dtype=np.float64).ravel()

    if x.size == 0:
        raise ValueError("samples must contain at least one element")
    if sampling_period <= 0:
        raise ValueError("sampling_period must be positive")

    n = x.size
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=sampling_period)

    # Single-sided amplitude scaling: DC and Nyquist keep 1/n, others 2/n.
    spectrum = spectrum / n
    spectrum[1:] *= 2
    if n % 2 == 0:
        spectrum[-1] /= 2  # Nyquist bin is not duplicated

    return freqs, spectrum


