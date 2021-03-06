import os
import csv
import pandas as pd
import numpy as np
import glob


# Goal: Collect 10,000 reviews, with 2,000 reviews in each category


def merge_data(scraped_data_dir="scraped_data/", num_samples=10000,
               random_state=1234):
    '''
    First, combine all restaurant reviews into one dataframe.
    Then, group each review by rating and randomly sample 2,000
    reviews from each group. Header argument is determined if
    there is header column in each CSV file from scraped data.

    Return: DataFrame with equal distribution of ratings
    '''
    # Get a list of all CSV filenames in scraped data directory
    all_rest_csv = [scraped_data_dir + file_name for file_name
                    in os.listdir(scraped_data_dir)
                    if file_name.endswith(".csv")]

    # Concatenate all DataFrames together
    df_from_each_file = (pd.read_csv(f, usecols=[0, 1],
                                     names=["Rating", "Text"],
                                     header=None)
                         for f in all_rest_csv)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)

    # Select (num_samples / 5) from each rating group
    num_samples_per_rating = round(num_samples / 5)
    concat_data = (concatenated_df.groupby("Rating")
                   .sample(n=num_samples_per_rating,
                           random_state=random_state)
                   .reset_index(drop=True))

    # Write concat_data to CSV
    concat_data.to_csv("merged_data.csv", header=False, index=False)
