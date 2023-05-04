import time
import numpy as np
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import scipy.signal
import mouse 

# Define the high pass filter
def apply_high_pass_filter(data, lowcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    b, a = butter(order, low, btype='high')
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Define the notch filter
def apply_notch_filter(data, notch_freq, fs, q=30):
    nyquist = 0.5 * fs
    freq = notch_freq / nyquist
    b, a = scipy.signal.iirnotch(freq, q)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Initialize board
params = BrainFlowInputParams()
params.serial_port = 'COM3'
board_id = BoardIds.CYTON_BOARD.value
board = BoardShim(board_id, params)

# Prepare board for streaming
board.prepare_session()

# Start data stream
board.start_stream()

# EMG channel indices for Cyton board (channels 1, 2, 3, and 4)
emg_channels = [1, 2, 3, 4]

# Set up matplotlib for real-time plotting
plt.ion()
fig, ax = plt.subplots(4, 1, sharex=True)

# Collect data for a certain amount of time (e.g., 10 seconds)
collection_time =60
start_time = time.time()

# Filter settings
lowcut = 1  # Set the lowcut frequency for the high-pass filter (1 Hz is a common choice)
fs = BoardShim.get_sampling_rate(board_id)  # Get the sampling rate of the board
# Create an empty buffer for accumulating the data
emg_data_buffer = None

while time.time() - start_time < collection_time:
    # Read data from the buffer
    data = board.get_current_board_data(1024)

    # Extract EMG channel data
    emg_data = data[emg_channels, :]

    # Accumulate data in the buffer
    if emg_data_buffer is None:
        emg_data_buffer = emg_data
    else:
        emg_data_buffer = np.hstack((emg_data_buffer, emg_data))
    # Check if we have enough data in the buffer
    if emg_data_buffer.shape[1] >= 50:
        
        # Apply high-pass filter to remove DC offset
        filtered_emg_data = apply_high_pass_filter(emg_data_buffer, lowcut, fs)

        # Apply notch filter to remove 50 Hz noise
        notch_freq=50
        filtered_emg_data = apply_notch_filter(filtered_emg_data, notch_freq, fs)

        # Update the plot with the filtered data
        for i, channel_data in enumerate(filtered_emg_data):
            ax[i].clear()
            ax[i].plot(channel_data)
            ax[i].set_title(f'Channel {emg_channels[i]}')
            ax[i].set_ylim(-250,250)
        plt.pause(0.01)

        

        # Clear the buffer
        emg_data_buffer = None

# Stop data stream and release the board
board.stop_stream()
board.release_session()