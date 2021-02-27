
import os
import csv
import pandas as pd
import numpy as np
import glob

# motivation: collect 10,000 reviews, with 2000 reviews in each category


def merge_data(scraped_data_dir='scraped_data/', num_samples=10000,
               random_state=1234, write_to_csv=True):
    '''
    First, we will combine all restaurant reviews into one dataframe. Then, we 
    will group each review by rating, then select 2000 reviews from each group 
    randomly. Header argument is determined if there is header column in each 
    csv file from scraped data.

    Return: Dataframe with equal distribution of reviews.
    '''
    # get a list of all csv filenames in scraped data directory
    all_rest_csv = [scraped_data_dir + file_name for file_name in os.listdir(
        scraped_data_dir) if file_name.endswith('.csv')]

    # concat all dataframes together
    df_from_each_file = (pd.read_csv(f) for f in all_rest_csv)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)

    # select (num_samples / 5 samples) from each rating group
    num_samples_per_rating = round(num_samples/5)
    concat_data = concatenated_df.groupby("Rating").sample(
        n=num_samples_per_rating, random_state=1234).reset_index(drop=True)

    # write concat_data to csv
    concat_data.to_csv('merged_data.csv', header=False, index=False)

    return None
