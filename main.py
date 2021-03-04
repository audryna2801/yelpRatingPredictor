from analyze_words import *
from model import *

import sys
import json
import joblib


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
        final_model = joblib.load("perfect_model.pkl")
        prediction = predictModel(final_model, [x_array])
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
    with open("columns.json") as f:
        columns = json.load(f)
    with open("idf.json") as f:
        idf = json.load(f)
    with open("combination.json") as f:
        comb = json.load(f)
    with open("stop_words.json") as f:
        stop_words = json.load(f)

    processed_input = processing(user_input, comb["lemmatize"])

    if comb['stop_word'] > 0:
        processed_input = [token for token in processed_input
                           if token not in stop_words]

    ngrams = make_ngrams(processed_input, comb["ngram"])
    tf = compute_tf(ngrams)

    ngrams_set = set(ngrams)
    columns_set = set(columns)
    indices = pd.Index(columns)

    x_array = np.zeros(len(columns))

    for token in ngrams_set:
        if token in columns_set:
            tfidf = tf[token] * idf[token]
            index = indices.get_loc(token)
            x_array[index] = tfidf

    return x_array


def compute_tf(doc):
    '''
    Compute the augmented term frequency (tf) of the tokens
    in a document.

    Inputs: 
      - doc (list of str): a list of tokens

    Returns: dict mapping terms to tf values
    '''
    token_dict = count_tokens(doc)
    tf_dict = {}
    max_count = max(token_dict.values())

    for token, count in token_dict.items():
        tf_dict[token] = 0.5 + 0.5 * (count / max_count)

    return tf_dict


if __name__ == "__main__":
    user_interface()