import sys
import joblib
import pandas as pd
import numpy as np
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
        prediction = final_model.predict(x_array)
        star_rating = int(prediction)

        print(" ")
        print("Your suggested star rating is: {}".format(star_rating))
        print(" ")
        print("Thank you for using our Suggested Star Rating System!")
    except EOFError:
        sys.exit()


def process_input(review):
    '''
    Autocorrects user input and converts it into a tfidf array
    using the saved vectorizer and selector PKL files.

    Inputs:
      - review (str): review input by user

    Returns: arr
    '''
    vectorizer = joblib.load("optimal_args/vectorizer.pkl")
    selector = joblib.load("optimal_args/selector.pkl")

    # Fix spelling errors
    textBlb = TextBlob(review)
    corrected_review = str(textBlb.correct())

    x_array = selector.transform(vectorizer.transform([corrected_review]))

    return x_array


if __name__ == "__main__":
    user_interface()
