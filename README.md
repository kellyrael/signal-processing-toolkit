# Signal Processing Toolkit

A small Python toolkit for generating synthetic time-domain signals, computing their frequency spectrum via FFT, and measuring signal frequency through threshold-based edge detection.

## Overview

This project demonstrates a simple signal-processing pipeline made up of three independent, composable modules:

| Module | Purpose |
|---|---|
| [acquire_pin.py](acquire_pin.py) | Simulates acquisition of a signal from a given "pin", generating a synthetic sinusoidal waveform sampled at a fixed period. |
| [compute_fft.py](compute_fft.py) | Computes the single-sided FFT (frequency spectrum) of a real-valued time-domain signal. |
| [find_average_frequency.py](find_average_frequency.py) | Detects rising-edge threshold crossings in a signal and computes the average frequency, period, jitter, and related statistics. |

## Requirements

- Python 3.9+
- Dependencies listed in [requirements.txt](requirements.txt):
  - `numpy>=1.24`
  - `matplotlib>=3.7`
  - `pytest>=7.4` (for running tests)

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Usage

### Acquire a signal

```python
from acquire_pin import acquire_pin

sampling_period = 1 / 1000  # seconds
signal = acquire_pin(pin_number=1, sampling_period=sampling_period)
```

### Compute the FFT

```python
from compute_fft import compute_fft

freqs, spectrum = compute_fft(signal, sampling_period)
```

### Measure average frequency

```python
from find_average_frequency import average_frequency

result = average_frequency(signal, sampling_period, threshold=0.0)
print(result["frequency"], "Hz")
```

## API Reference

### `acquire_pin(pin_number, sampling_period)`

Generates a 1-second synthetic signal for the given pin number:

- `pin_number == 1`: sum of 50 Hz and 120 Hz sine components.
- `pin_number == 2`: a 250 Hz sine component.
- otherwise: a 600 Hz sine component.

Returns a `np.ndarray` of samples.

### `compute_fft(samples, sampling_period)`

Computes the single-sided amplitude spectrum of a real-valued signal using `numpy.fft.rfft`.

Returns `(freqs, spectrum)`, where `freqs` are frequency bins in Hz and `spectrum` contains the corresponding complex FFT coefficients scaled to signal amplitude.

Raises `ValueError` if `samples` is empty or `sampling_period` is not positive.

### `average_frequency(samples, sampling_period, threshold, hysteresis=0.0, interpolate=True)`

Detects rising-edge crossings of `threshold` and returns a dictionary describing the measured frequency:

- `frequency`, `period` — averaged over all detected cycles.
- `edge_times`, `edge_indices` — crossing locations.
- `cycles`, `periods`, `jitter` — per-cycle statistics.
- `span` — index range spanned by the first and last edge.

Supports optional hysteresis (to reject noise-triggered edges) and sub-sample linear interpolation of crossing times.

Raises `ValueError` for invalid parameters or if fewer than two rising edges are found.

## Testing

Tests are written with `pytest`. Run the full suite with:

```bash
pytest
```

See [TEST_PLAN.md](TEST_PLAN.md) for the detailed test strategy and case list.

## Project Structure

```
.
├── acquire_pin.py
├── compute_fft.py
├── find_average_frequency.py
├── requirements.txt
├── README.md
├── TEST_PLAN.md
└── .gitignore
```

## License

This project is provided as-is for demonstration purposes.
