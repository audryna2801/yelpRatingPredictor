import os
import csv
import pandas as pd
import numpy as np
import glob

SCRAPED_DATA = ["scraped_data/boston/", "scraped_data/la/", "scraped_data/nyc/",
                "scraped_data/phil/", "scraped_data/chi/", "scraped_data/lav/",
                "scraped_data/miami/", "scraped_data/sf/", "scraped_data/houston/"]


def merge_data(out_csv, scraped_data_dirs=SCRAPED_DATA, num_samples=10000,
               random_state=33):
    '''
    First, combine all restaurant reviews into one dataframe.
    Then, it will try to generate equal (or most equal) distribution of reviews
    per rating. Merged dataset is then written into a csv.

    Input:
      - out_csv (str): csv file name for the merged dataset
      - scraped_data_dir (dir): directory containing food reviews from 
                                restaurants
      - num_samples (int): total number of reviews selected for merged dataset
      - random_state (int): seed for random sampling

    Returns: None, writes to CSV file
    '''
    # Get a list of all CSV filenames in scraped data directories
    all_rest_csv = []

    for directory in SCRAPED_DATA:
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
    for rating in range(1, 6):
        ideal_size = round(remaining_samples / (6 - rating))
        rating_df = concatenated_df[concatenated_df.Rating == rating]
        rating_size = rating_df.shape[0]
        size = min(ideal_size, rating_size)
        rating_sample = rating_df.sample(size, random_state=random_state)
        final_df = pd.concat([final_df, rating_sample], ignore_index=True)
        remaining_samples -= size

    # Write concat_data to CSV
    final_df.to_csv(out_csv, index=False)
