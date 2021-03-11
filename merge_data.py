import os
import csv
import pandas as pd
import numpy as np
import glob

SCRAPED_DATA = ["scraped_data/boston/", "scraped_data/la/", "scraped_data/nyc/",
                "scraped_data/phil/", "scraped_data/chi/", "scraped_data/lav/",
                "scraped_data/miami/", "scraped_data/sf/", "scraped_data/houston/"]


def merge_data(scraped_data_dirs=SCRAPED_DATA, num_samples=10000,
               random_state=1234):
    '''
    First, combine all restaurant reviews into one dataframe.
    Then, it reduces overweight of 5 star reviews by removing them.
    Merged dataset is then written into a csv.

    Input:
        scraped_data_dir (dir): directory containing food reviews from 
                                restaurants
        num_samples (int): total number of reviews selected for merged dataset
        random_state (int): seed for random sampling
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

    # Reducing overweight of five star reviews by removing some of them
    num_to_remove = concatenated_df.shape[0] - num_samples
    five_star = concatenated_df[concatenated_df.Rating == 5]
    five_star_to_remove = five_star.sample(n=num_to_remove,
                                           random_state=random_state)
    final_df = pd.concat([concatenated_df,
                          five_star_to_remove]).drop_duplicates(keep=False)

    # The below code was used previously to get an equal
    # distribution of review per rating

    ## num_samples_per_rating = round(num_samples / 5)

    # concat_data = (concatenated_df.groupby("Rating").sample(
    # n=num_samples_per_rating, random_state=random_state).reset_index(drop=True))

    # Write concat_data to CSV
    final_df.to_csv("merged_data_testing.csv", index=False)
