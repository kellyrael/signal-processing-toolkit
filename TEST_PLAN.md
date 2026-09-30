# Test Plan — Signal Processing Toolkit

## 1. Purpose and Scope

This test plan defines the strategy, environment, and detailed test cases for verifying the correctness of the Signal Processing Toolkit, covering:

- [acquire_pin.py](acquire_pin.py) — synthetic signal generation
- [compute_fft.py](compute_fft.py) — FFT / spectrum computation
- [find_average_frequency.py](find_average_frequency.py) — edge-detection frequency measurement

Out of scope: plotting/visual output correctness (`matplotlib` rendering), performance/load testing, and GUI testing.

## 2. Test Objectives

- Verify each function produces mathematically correct output for known inputs.
- Verify input validation raises the documented exceptions for invalid arguments.
- Verify edge cases (empty/short arrays, boundary sample counts, noisy signals) are handled correctly.
- Verify the three modules integrate correctly end-to-end (acquire → FFT → frequency measurement).

## 3. Test Approach

- **Framework:** `pytest` (already listed in [requirements.txt](requirements.txt)).
- **Type of testing:** Automated unit tests, with a small number of integration tests chaining the modules together.
- **Test data:** Synthetic signals generated with `numpy`, with analytically known frequency/amplitude, so expected results can be computed independently of the code under test.
- **Assertions:** Use `numpy.testing.assert_allclose` / `pytest.approx` for floating-point comparisons with explicit tolerances.
- **Structure:** One test module per source module:
  - `test_acquire_pin.py`
  - `test_compute_fft.py`
  - `test_find_average_frequency.py`
  - `test_integration.py`

## 4. Test Environment

- Python 3.9+
- Dependencies from [requirements.txt](requirements.txt): `numpy`, `matplotlib`, `pytest`
- No external services, network access, or hardware required (all signals are synthetic).
- Run locally via: `pytest -v`

## 5. Entry / Exit Criteria

**Entry criteria:**
- Dependencies installed per [README.md](README.md).
- Source modules import without error.

**Exit criteria:**
- 100% of test cases in this plan pass.
- No unhandled exceptions for any documented valid input.
- All documented `ValueError` conditions are confirmed to raise.

## 6. Detailed Test Cases

### 6.1 `acquire_pin(pin_number, sampling_period)`

| ID | Description | Input | Expected Result |
|---|---|---|---|
| AP-01 | Pin 1 returns composite 50/120 Hz signal of correct length | `pin_number=1, sampling_period=0.001` | `len(sig) == 1000`; signal matches `3*sin(2π·50·t) + 1.5*sin(2π·120·t)` within tolerance |
| AP-02 | Pin 2 returns expected waveform | `pin_number=2, sampling_period=0.001` | Signal matches `3*sin(5π·100·t)` within tolerance |
| AP-03 | Any other pin number returns the default waveform | `pin_number=99, sampling_period=0.001` | Signal matches `3*sin(6π·200·t)` within tolerance |
| AP-04 | Output length scales with sampling period | `sampling_period=0.01` | `len(sig) == 100` |
| AP-05 | Return type is a numpy array of floats | any valid input | `isinstance(sig, np.ndarray)` and `sig.dtype == float64` |

### 6.2 `compute_fft(samples, sampling_period)`

| ID | Description | Input | Expected Result |
|---|---|---|---|
| CF-01 | Single-tone signal produces a spectral peak at the correct frequency | 50 Hz sine, `fs=1000 Hz`, 1 s duration | `freqs[argmax(abs(spectrum))] ≈ 50 Hz` |
| CF-02 | Peak amplitude matches the input sinusoid amplitude | `A * sin(2π·f·t)` | `max(abs(spectrum)) ≈ A` (within tolerance) |
| CF-03 | Frequency bins are non-negative and span 0..Nyquist | any valid input | `freqs.min() == 0`, `freqs.max() <= fs/2` |
| CF-04 | DC component detected for constant-offset signal | `samples = constant + sine` | `spectrum[0] ≈ constant` |
| CF-05 | Multi-tone signal resolves both frequencies | 50 Hz + 120 Hz composite (as in AP-01) | Peaks detected near both 50 Hz and 120 Hz |
| CF-06 | Even-length input halves the Nyquist bin correctly | `n` even | No exception; `spectrum[-1]` reflects halved Nyquist scaling |
| CF-07 | Odd-length input | `n` odd | No exception; correct-length output arrays |
| CF-08 | Empty `samples` raises `ValueError` | `samples=[]` | `ValueError` raised |
| CF-09 | Non-positive `sampling_period` raises `ValueError` | `sampling_period=0` and `sampling_period=-1` | `ValueError` raised in both cases |
| CF-10 | Accepts list/array-like input, not only `np.ndarray` | `samples` as Python list | No exception; correct result |

### 6.3 `average_frequency(samples, sampling_period, threshold, hysteresis, interpolate)`

| ID | Description | Input | Expected Result |
|---|---|---|---|
| AF-01 | Correct frequency for a clean sine wave | 50 Hz sine, `fs=1000 Hz`, `threshold=0` | `result["frequency"] ≈ 50` (within tolerance) |
| AF-02 | Correct edge count for a known number of cycles | 10-cycle signal | `result["cycles"] == 9` (edge-to-edge intervals = cycles - 1) |
| AF-03 | Interpolation improves accuracy vs. no interpolation | same signal, `interpolate=True` vs `False` | Interpolated frequency closer to the true frequency |
| AF-04 | Hysteresis suppresses noise-triggered edges | sine + small high-frequency noise near threshold | With `hysteresis>0`, edge count matches clean-signal case; with `hysteresis=0`, spurious edges may appear |
| AF-05 | Jitter is ~0 for a perfectly periodic signal | clean sine | `result["jitter"] ≈ 0` |
| AF-06 | `span` reflects first/last edge indices | any valid input | `result["span"] == (edge_indices[0], edge_indices[-1])` |
| AF-07 | Fewer than 2 rising edges raises `ValueError` | flat/constant signal, or signal with only 1 edge | `ValueError` raised |
| AF-08 | Non-positive `sampling_period` raises `ValueError` | `sampling_period=0` | `ValueError` raised |
| AF-09 | Negative `hysteresis` raises `ValueError` | `hysteresis=-1` | `ValueError` raised |
| AF-10 | Fewer than 2 samples raises `ValueError` | `samples=[1.0]` | `ValueError` raised |
| AF-11 | Threshold crossing exactly at a sample (no interpolation ambiguity) | constructed signal with an exact-threshold sample | No exception; correct edge index |

### 6.4 Integration Tests

| ID | Description | Steps | Expected Result |
|---|---|---|---|
| IT-01 | End-to-end pin 1 signal → FFT peaks at 50 Hz and 120 Hz | `acquire_pin(1, T)` → `compute_fft` | Two dominant peaks at ~50 Hz and ~120 Hz |
| IT-02 | End-to-end pin 2 signal → measured average frequency matches expected tone | `acquire_pin(2, T)` → `average_frequency` | Measured frequency close to the analytical frequency of pin 2's waveform |
| IT-03 | Pipeline is stable across all three pin numbers | Run acquire → FFT → average_frequency for pins 1, 2, 3 | No exceptions; results consistent with each waveform's known frequency content |

## 7. Risks / Assumptions

- Floating-point comparisons require explicit tolerances (`rtol`/`atol`); exact equality is not expected.
- `find_average_frequency` accuracy depends on `sampling_period` resolution relative to signal frequency (aliasing risk for very high frequencies, e.g., pin 3's 300 Hz component sampled per `acquire_pin`'s defaults).
- Tests assume synthetic, noise-free signals unless explicitly testing hysteresis/noise handling.

## 8. Deliverables

- `test_acquire_pin.py`, `test_compute_fft.py`, `test_find_average_frequency.py`, `test_integration.py` implementing the cases above.
- Passing `pytest` run with no failures or errors as the acceptance criterion for release.
