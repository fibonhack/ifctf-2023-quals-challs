# Decomment to parse from IQ samples file
sample_rate = 20e6
sample_period = 1/sample_rate
symbol_period = 200e-6
samples_per_symbol = int(sample_rate * symbol_period)
center_frequency = 438_671_600
signal_freq = 434e6
low_pass_cutoff = 10e3
static_gain = 80

# Read samples from file
samples = np.fromfile('gqrx_20230604_224801_438671600_20000000_fc.raw', dtype=float)
N = len(samples)
print(f"Loaded {N} samples")

# Shift
t = sample_period * np.arange(N)
shift_freq = center_frequency - signal_freq
sin = np.cos(2*np.pi*(shift_freq)*t)
samples = samples * sin
print(f"Shifted signal by {shift_freq}Hz")

# Low pass
from scipy.signal import butter, filtfilt

# Design the filter
order = 2  # Filter order
nyquist_freq = 0.5 * sample_rate
normalized_cutoff = low_pass_cutoff / nyquist_freq
b, a = butter(order, normalized_cutoff, btype='low', analog=False)

# Apply the filter to the signal
chunk_size = 1_000_000
filtered_signal = np.zeros_like(samples)
for i in range(0, len(samples), chunk_size):
    chunk = samples[i:i+chunk_size]
    chunk = filtfilt(b, a, chunk)
    filtered_signal[i:i+chunk_size] = chunk

samples = filtered_signal
print(f"Filtered out the signal with cutoff {low_pass_cutoff}")

# Magnitude
samples = np.abs(samples)
print(f"Got signal amplitude")

# Amplify
samples = samples * static_gain
print(f"Amplified signal by {static_gain}")

# Threshold
chunk_size = 1_000_000
thresholded_signal = np.zeros_like(samples)
for i in range(0, len(samples), chunk_size):
    chunk = samples[i:i+chunk_size]
    chunk = np.where(chunk > 0.5, 1, 0)
    thresholded_signal[i:i+chunk_size] = chunk

samples = thresholded_signal
data = bytearray(samples.astype(int))

with open("test_output.txt", "wb") as f:
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i+chunk_size]
        f.write(chunk)

exit()