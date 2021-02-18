from analyze_words import *

# Code to get user input
# ....

# Process user input


def main(user_input, remove_stop=True, stop_words, idf):
    processed_input = processing(user_input)

    if remove_stop:
        processed_input = remove_stop(stop_words, processed_input)

    ngrams = make_ngrams(processed_input, n)

    # Issue with vectorizing, need to follow order of the vector before
    for token in list(ngrams):
        if token not in idf:
            ngrams.remove(token)

    # more code to vectorize the given input
