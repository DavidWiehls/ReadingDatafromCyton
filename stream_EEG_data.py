import data_from_EEG_channels as unicorn



collection_time = 3600
unicorn.stream_data(collection_time)

#cyton.save_data(collection_time, "test.csv")

print('Done')