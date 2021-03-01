from analyze_words import *
import sys


# Code to get user input
# ....

# Process user input


def user_stuff_here():
    print("===================================================")
    print("   Welcome to the Suggested Star Rating System!")
    print()
    print("            Copy and paste your review.")
    print()
    print("      Press Control-D to exit or type quit()")
    print("===================================================")
    print()

    review = input("Enter review here: ")
    review = str(review)
    
    
    if type(review) == str:
        if len(review) >= 50:
            pass
            vectorized_review = main(review, remove_stop=True, stop_words, idf, columns)
            #run function, s.t star_rating = some int/5
        else:
            print("Please input a longer review.")

    else: 
        print("Please enter a valid input.")
    
    print("Your suggest star rating is:", star_rating)
    print("Thank you for using our Suggested Star Rating System!")
    print(quit)

def main(user_input, stop_words=10, idf, columns, n_grams):
    processed_input = processing(user_input)

    if stop_words == 0:
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
