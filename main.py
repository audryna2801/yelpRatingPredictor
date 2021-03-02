from analyze_words import *
from model import *
import sys
import json
import joblib
import nltk
nltk.download('wordnet')

def user_interface():
    print("===================================================")
    print("   Welcome to the Suggested Star Rating System!")
    print()
    print("            Copy and paste your review.")
    print()
    print("       Type Control-D to exit the program.")
    print("===================================================")
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
        final_model = joblib.load("final_model.pkl")
        prediction = predictModel(final_model, [x_array])
        star_rating = int(prediction)

        print("Your suggested star rating is: {}".format(str(star_rating)))
        print("Thank you for using our Suggested Star Rating System!")
    except EOFError:
        sys.exit()



def process_input(user_input):
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
        processed_input = [
            token for token in processed_input if token not in stop_words]

    ngrams = make_ngrams(processed_input, comb["ngram"])
    tf = augmented_freq(ngrams)

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


if __name__ == "__main__":
    user_interface()
