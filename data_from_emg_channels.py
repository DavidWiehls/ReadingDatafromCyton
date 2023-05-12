import time
import numpy as np
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import scipy.signal
import mouse
import arduino_api as Arduino

print("import done")
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

# Define a function to check if the difference in data values is greater than the threshold for specific channel combinations
def check_threshold(filtered_emg_data, samples_per_100ms, threshold):
    channels_meeting_threshold = [False for _ in range(len(filtered_emg_data))]
    
    for i, channel_data in enumerate(filtered_emg_data):
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

# Filter settings
lowcut = 5  # Set the lowcut frequency for the band-pass filter
highcut = 50  # Set the highcut frequency for the band-pass filter
notch_freq=50 # Set the notch frequency (50Hz or 60Hz)

fs = BoardShim.get_sampling_rate(board_id)  # Get the sampling rate of the board
# Create an empty buffer for accumulating the data
emg_data_buffer = None

# Calculate the number of samples for 0.1 seconds
samples_per_100ms = int(0.1 * fs)

# Call the function to check the threshold for the filtered EMG data
threshold = 80

# Collect data for a certain amount of time

def stream_data(collection_time):
    emg_data_buffer = None
    
    start_time = time.time()
    while time.time() - start_time <= collection_time:

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
            # Apply notch filter to remove 50 Hz noise
            filtered_emg_data = apply_notch_filter(emg_data_buffer, notch_freq, fs)
            # Apply band-pass filter
            filtered_emg_data = apply_bandpass_filter(filtered_emg_data, lowcut, highcut, fs)

            # Call the function to check the threshold for the filtered EMG data
            scenarios_met = check_threshold(filtered_emg_data, samples_per_100ms, threshold)
            hand_gestures(scenarios_met)
            # Place HERE the funtion that uses the streamed emg signal
            #hand_gestures(scenarios_met)            

            # Update the plot with the filtered data
            for i, channel_data in enumerate(filtered_emg_data):
                ax[i].clear()
                ax[i].plot(channel_data)
                ax[i].set_title(f'Channel {emg_channels[i]}')
                ax[i].set_ylim(-250,250)
            plt.pause(0.01)

            # Clear buffer
            emg_data_buffer = None
        
    # Stop data stream and release the board
    board.stop_stream()
    board.release_session()

def save_data(collection_time, filename):
    time.sleep(collection_time)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    emg_data = data[emg_channels, :]

    filtered_emg_data = apply_bandpass_filter(emg_data_buffer, lowcut, highcut, fs)
    # Apply notch filter to remove 50 Hz noise
    filtered_emg_data = apply_notch_filter(filtered_emg_data, notch_freq, fs)

    append_data_to_csv(filename, filtered_emg_data)


    board.stop_stream()
    board.release_session()

def move_mouse(scenarios_met):
    # Check the scenarios and move the mouse accordingly
    if scenarios_met[0]:  # Scenario 1: Channel 1 and 2 meet the threshold
        current_position = mouse.get_position()
        new_position = (current_position[0], current_position[1]-30)
        mouse.move(*new_position)
        print("Scenario 1: Mouse moved down.")
    elif scenarios_met[1]:  # Scenario 2: Channel 2 and 3 meet the threshold
        current_position = mouse.get_position()
        new_position = (current_position[0], current_position[1] +30)
        mouse.move(*new_position)
        print("Scenario 2: Mouse moved up.")
    elif scenarios_met[2]:  # Scenario 3: Channel 1,2,3 and 4 meet the threshold
        current_position = mouse.get_position()
        new_position = (current_position[0]+30, current_position[1])
        mouse.move(*new_position)
        print("Scenario 3: Mouse move to the right.")
    else:
        print("None of the scenarios are met.")

def hand_gestures(scenarios_met):
    if scenarios_met[2]:
        Arduino.hand_position1()
        print("Hand is closed")
    elif scenarios_met[0]:
        Arduino.hand_position2()
        print("Rock and Roll")
    else:
        Arduino.initial_position()
        print("Hand is open")
    