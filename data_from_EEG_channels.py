import time
import numpy as np
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import scipy.signal


# Define the bandpass filter
def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Define the notch filter
def apply_notch_filter(data, notch_freq, fs, q=30):
    nyquist = 0.5 * fs
    freq = notch_freq / nyquist
    b, a = scipy.signal.iirnotch(freq, q)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Append the data from the buffer 
def append_data_to_csv(filename, data):
    with open(filename, 'ab') as f:
        np.savetxt(f, data.T, delimiter = ',')

# Power spectrum of the EEG channels
def power_spectrum(data, fs):
    freqs = np.fft.rfftfreq(len(data), 1/fs)
    power = np.abs(np.fft.rfft(data))**2
    return freqs, power

# Define a function to check if the difference in data values is greater than the threshold for specific channel combinations
def check_threshold(filtered_eeg_data, samples_per_100ms, threshold):
    channels_meeting_threshold = [False for _ in range(len(filtered_eeg_data))]
    
    for i, channel_data in enumerate(filtered_eeg_data):
        # Compute the difference in data values for the current channel
        difference = np.abs(np.diff(channel_data[-samples_per_100ms:]))
        
        # Check if all differences are greater than the lower_threshold
        if np.any(difference > threshold):
            channels_meeting_threshold[i] = True
            
    scenario1 = channels_meeting_threshold[0] and channels_meeting_threshold[1] and not channels_meeting_threshold[2] and not channels_meeting_threshold[3]
    scenario2 = channels_meeting_threshold[3] and not channels_meeting_threshold[0] and not channels_meeting_threshold[1] and not channels_meeting_threshold[2]
    scenario3 = channels_meeting_threshold[0] and channels_meeting_threshold[1] and channels_meeting_threshold[2] and channels_meeting_threshold[3]
    
    return [scenario1, scenario2, scenario3]

# Initialize board
params = BrainFlowInputParams()
print("init")
params.serial_port = 'COM5'
board_id = BoardIds.UNICORN_BOARD.value
params.serial_number = 'UN-2019.06.78'
board = BoardShim(board_id, params)

# Prepare board for streaming
board.prepare_session()

# Start data stream
board.start_stream()

# eeg channel indices for Cyton board (channels 1, 2, 3, and 4)
eeg_channels = [0, 1, 2, 3, 4, 5, 6, 7]

# Filter settings
lowcut = 2  # Set the lowcut frequency for the band-pass filter
highcut = 30  # Set the highcut frequency for the band-pass filter
notch_freq=50 # Set the notch frequency (50Hz or 60Hz)

fs = BoardShim.get_sampling_rate(board_id)  # Get the sampling rate of the board
# Create an empty buffer for accumulating the data
eeg_data_buffer = None

# Collect data for a certain amount of time

# def stream_data(collection_time):
#     eeg_data_buffer = None

#     # Set up matplotlib for real-time plotting
#     plt.ion()
#     fig, ax = plt.subplots(8, 1, sharex=True) # Create ne suplots for the channels
#     power_spectrum_fig, power_spectrum_ax = plt.subplots()  # Create single plot for the power spectrum

#     start_time = time.time()
#     while time.time() - start_time <= collection_time:

#         # Read data from the buffer
#         data = board.get_current_board_data(1024)
#         # Extract eeg channel data
#         eeg_data = data[eeg_channels, :]

#         # Accumulate data in the buffer
#         if eeg_data_buffer is None:
#             eeg_data_buffer = eeg_data
#         else:
#             eeg_data_buffer = np.hstack((eeg_data_buffer, eeg_data))



#         # Check if we have enough data in the buffer
#         if eeg_data_buffer.shape[1] >= 100:
#             # Apply notch filter to remove 50 Hz noise
#             filtered_eeg_data = apply_notch_filter(eeg_data_buffer, notch_freq, fs)
#             # Apply band-pass filter
#             filtered_eeg_data = apply_bandpass_filter(filtered_eeg_data, lowcut, highcut, fs)

#             # Call the function to check the threshold for the filtered eeg data

#             # Update the plot with the filtered data
#             for i, channel_data in enumerate(filtered_eeg_data):
#                 ax[i].clear()
#                 ax[i].plot(channel_data)
#                 ax[i].set_title(f'Channel {eeg_channels[i]+1}')
#                 ax[i].set_ylim(-50,50)

#                 # Calculate and plot the power spectrum
#                 freqs, power = power_spectrum(channel_data, fs)
#                 power_spectrum_ax[i].clear()
#                 power_spectrum_ax[i].semilogy(freqs, power)
#                 power_spectrum_ax[i].set_title(f'Power Spectrum Channel {eeg_channels[i]+1}')
#                 power_spectrum_ax[i].set_xlabel('Frequency [Hz]')
#                 power_spectrum_ax[i].set_ylabel('Power')
#                 power_spectrum_ax[i].set_xlim(0, highcut)  # Show up to the highcut frequency
#             plt.pause(0.01)
#             # Clear buffer
#             eeg_data_buffer = None
        
#     # Stop data stream and release the board
#     board.stop_stream()
#     board.release_session()

def stream_data(collection_time):
    eeg_data_buffer = None
    power_spectrum_fig, power_spectrum_ax = plt.subplots()  # Create single plot for the power spectrum
    
    start_time = time.time()
    while time.time() - start_time <= collection_time:

        # Read data from the buffer
        data = board.get_current_board_data(2048)
        # Extract eeg channel data
        eeg_data = data[eeg_channels, :]

        # Accumulate data in the buffer
        if eeg_data_buffer is None:
            eeg_data_buffer = eeg_data
        else:
            eeg_data_buffer = np.hstack((eeg_data_buffer, eeg_data))

        # Check if we have enough data in the buffer
        if eeg_data_buffer.shape[1] >= 100:
            # Apply notch filter to remove 50 Hz noise
            filtered_eeg_data = apply_notch_filter(eeg_data_buffer, notch_freq, fs)
            # Apply band-pass filter
            filtered_eeg_data = apply_bandpass_filter(filtered_eeg_data, lowcut, highcut, fs)

            # Update the plot with the filtered data
            power_spectrum_ax.clear()
            for i, channel_data in enumerate(filtered_eeg_data):
                # Calculate and plot the power spectrum
                freqs, power = power_spectrum(channel_data, fs)
                power_spectrum_ax.semilogy(freqs, power, label=f'Channel {eeg_channels[i]+1}')
                
            power_spectrum_ax.set_title('Power Spectrum')
            power_spectrum_ax.set_xlabel('Frequency [Hz]')
            power_spectrum_ax.set_ylabel('Power')
            power_spectrum_ax.set_ylim(10**0, 10**10)
            power_spectrum_ax.set_xlim(0, highcut)  # Show up to the highcut frequency
            power_spectrum_ax.legend()  # Add legend to distinguish the channels

            plt.pause(0.01)

            # Clear buffer
            eeg_data_buffer = None
        
    # Stop data stream and release the board
    board.stop_stream()
    board.release_session()
