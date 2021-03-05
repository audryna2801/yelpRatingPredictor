import sys
import json
import joblib
import pandas as pd
import numpy as np
from analyze_words import processing, make_ngrams, count_tokens
from sklearn import linear_model
from textblob import TextBlob


def user_interface():
    '''Prompt user to input a review, and suggest a star rating.'''
    print("==================================================")
    print("   Welcome to the Suggested Star Rating System!")
    print()
    print("            Copy and paste your review.")
    print()
    print("       Type Control-D to exit the program.")
    print("==================================================")
    print()
    try:
        while True:
            review = input("Enter review here: ")
            review = str(review)
            if len(review) >= 50:
                break
            else:
                print("Please input a longer review.")

        x_array = process_input(review)

        final_model = joblib.load("optimal_args/final_model.pkl")
        prediction = final_model.predict([x_array])
        star_rating = int(prediction)

        print("Your suggested star rating is: {}".format(star_rating))
        print("Thank you for using our Suggested Star Rating System!")
    except EOFError:
        sys.exit()


def process_input(user_input):
    '''
    Convert a review input by the user into an array of zeros,
    where each item corresponding to a valid n-gram in the input
    is replaced by the n-gram's tfidf. This allows a review to be
    evaluated by a model.

    Inputs:
      - user_input (str): review input by user

    Returns: arr
    '''
    with open("optimal_args/columns.json") as f:
        column_names = json.load(f)
    with open("optimal_args/idf.json") as f:
        idf = json.load(f)
    with open("optimal_args/combination.json") as f:
        combi = json.load(f)
    with open("optimal_args/stop_words.json") as f:
        stop_words = json.load(f)

    # Fix spelling errors before prediction
    textBlb = TextBlob(user_input)
    corrected_user_input = textBlb.correct()
    print("Your review is: ", corrected_user_input)
    processed_input = processing(corrected_user_input, combi["lemmatize"])

    if combi["num_stop_words"] > 0:
        processed_input = [token for token in processed_input
                           if token not in stop_words]

    ngrams = make_ngrams(processed_input, combi["ngram"])
    token_counts = count_tokens(ngrams)
    max_count = max(token_counts.values())

    columns_set = set(column_names)
    indices = pd.Index(column_names)

    x_array = np.zeros(len(column_names))

    for token, count in token_counts.items():
        if token in columns_set:
            tf = 0.5 + 0.5 * (count / max_count)
            tfidf = tf * idf[token]
            index = indices.get_loc(token)
            x_array[index] = tfidf

    return x_array


if __name__ == "__main__":
    user_interface()
