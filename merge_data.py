import os
import csv
import pandas as pd
import numpy as np
import glob

SCRAPED_DATA = ["lav_scraped_data/", "chi_scraped_data/"]


def merge_data(scraped_data_dirs=SCRAPED_DATA, num_samples=10000,
               random_state=1234):
    '''
    First, combine all restaurant reviews into one dataframe.
    Then, group each review by rating and randomly sample 2,000
    reviews from each group. Merged dataset is then written into a csv.

    Input:
        scraped_data_dir (dir): directory containing food reviews from 
                                restaurants
        num_samples (int): total number of reviews selected for merged dataset
        random_state (int): seed for sampling reviews from each rating group 
                            [1-5]
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

    # # Select (num_samples / 5) from each rating group
    # num_samples_per_rating = round(num_samples / 5)

    # concat_data = (concatenated_df.groupby("Rating").sample(
    #     n=num_samples_per_rating, random_state=random_state).reset_index(drop=True))

    # Write concat_data to CSV
    concatenated_df.to_csv("merged_data_testing.csv", index=False)
