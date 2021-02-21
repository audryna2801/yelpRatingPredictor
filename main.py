from analyze_words import *

# Code to get user input
# ....

# Process user input


def user_stuff_here():

    pass


def main(user_input, remove_stop=True, stop_words, idf, columns):
    processed_input = processing(user_input)

    if remove_stop:
        processed_input = remove_stop(stop_words, processed_input)

    ngrams = make_ngrams(processed_input, n)
    ngram_set = set(ngrams)

    # Issue with vectorizing, need to follow order of the vector before
    for token in list(ngrams):
        if token not in idf:
            ngrams.remove(token)

    x_array = []
    for column in columns:
        if column in ngram_set:
            # calculate tfidf
        else:
            x_array.append(0)

    # more code to vectorize the given input
