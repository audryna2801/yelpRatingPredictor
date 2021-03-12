import os
import csv
import pandas as pd
import numpy as np
import glob

RANDOM_SEED = 33


def merge_data(out_csv="test_data/merged_data.csv",
               scraped_data_dir="scraped_data/", num_samples=5000):
    '''
    First, combine all restaurant reviews into one dataframe.
    Then, try to generate a roughly equal distribution of reviews
    in terms of rating. Finally, write merged dataset into a CSV.

    Input:
      - out_csv (str): csv file name for the merged dataset
      - scraped_data_dir (str): name of directory containing food reviews from 
                                restaurants in different cities
      - num_samples (int): total number of reviews selected for merged dataset

    Returns: None, writes to CSV file
    '''
    # Get a list of all CSV filenames in scraped data directories
    all_rest_csv = []

    for directory in os.listdir(scraped_data_dir):
        for file_name in os.listdir(directory):
            all_rest_csv += [str(directory+file_name)]

    # Concatenate all DataFrames together
    df_from_each_file = (pd.read_csv(f, usecols=[0, 1],
                                     names=["Rating", "Text"],
                                     header=None)
                         for f in all_rest_csv)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)

    # Removing duplicates if present
    concatenated_df = concatenated_df.drop_duplicates().reset_index(drop=True)

    # Try to achieve the most equal distribution of reviews by rating
    remaining_samples = num_samples
    final_df = pd.DataFrame()
    remaining_group = 5  # There is 5 rating groups
    for rating in range(1, 6):
        ideal_size = round(remaining_samples / remaining_group)
        rating_df = concatenated_df[concatenated_df.Rating == rating]
        rating_size = rating_df.shape[0]
        size = min(ideal_size, rating_size)
        rating_sample = rating_df.sample(size, random_state=RANDOM_SEED)
        final_df = pd.concat([final_df, rating_sample], ignore_index=True)
        remaining_samples -= size
        remaining_group -= 1

    # Write concat_data to CSV
    final_df.to_csv(out_csv, index=False)
