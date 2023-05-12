import data_from_EMG_channels as cyton
import arduino_api as Arduino


collection_time = 3600
cyton.stream_data(collection_time)

#cyton.save_data(collection_time, "test.csv")

print('Done')