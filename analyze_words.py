import math
import sys
import unicodedata
import pandas as pd
import re
import csv
import itertools
import string
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
# nltk.download("wordnet") --> uncomment if missing wordnet nltk library


# Generating global variables
STOP_PREFIXES = ("@", "#", "http", "&amp")
PUNCTUATION = string.punctuation + "…"  # Added the special character elipsis
INTERNAL_PUNCTUATION = set(PUNCTUATION) - {"'"}  # Want to keep apostrophe
LEMMATIZER = WordNetLemmatizer()


# Pre-processing stage
def processing(text):
    '''
    Convert a text of a review into a list of strings.

    Inputs:
      - text (str): text representing one review

    Returns: list of tokens
    '''
    text = re.sub("([^\x00-\x7F])+", " ", text)  # Remove non-English words
    split_text = text.split()
    new_text = []

    for word in split_text:
        # Handle trailing punctuation
        word = word.replace("&apos;", "'")
        word = word.replace("quot;", '"')
        word = word.replace("&quot", '"')
        word = word.strip(PUNCTUATION)

        # Handle internal punctuation
        word_set = set(word)
        punc_in_word = word_set.intersection(INTERNAL_PUNCTUATION)

        for punc in punc_in_word:
            word = word.replace(punc, " ")

        for word in word.split():
            word = word.lower()
            word = LEMMATIZER.lemmatize(word)
            if (word and not bool(re.search(r"\d", word))
                    and not word.startswith(STOP_PREFIXES)):
                new_text.append(word)

    return new_text


def get_stop_words(corpus, num_stop_words=20):
    '''
    Obtain the particular stop words (most frequently occurring
    words) in the sample, which may differ from those in a list
    of generic stop words.

    Line 80-83 adapted from 
    https://programminghistorian.org/en/lessons/analyzing-documents-with-tfidf

    Inputs:
      - corpus (list of str): list of reviews
      - num_stop_words (int): number of stop words to remove

    Returns: list of most common tokens
    '''
    count_vectorizer = CountVectorizer(tokenizer=processing)
    X = count_vectorizer.fit_transform(corpus)

    sum_words = X.sum(axis=0)
    words_freq = [(word, sum_words[0, idx])
                  for word, idx in count_vectorizer.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    words_freq_no_count = [word for word, _ in words_freq]

    return words_freq_no_count[:num_stop_words]


def get_df_idf_stops(csv_file, n, num_stop_words):
    '''
    Given a CSV file containing food reviews and rating, generate a
    tokenized array with tf_idf values. Also generate a series of
    the numerical ratings (y_values) and a vectorizer object.

    Inputs:
        csv_file (str): CSV file containing scraped Yelp reviews
        n (int): range of n-grams to use
        num_stop_words (int): number of stop words to remove

    Returns: list of array (X), series (y_values), 
             Vectorizer Obj (idf_vectorizer)
    '''
    df = pd.read_csv(csv_file)
    corpus = df.Text
    stop_words = get_stop_words(corpus, num_stop_words)

    idf_vectorizer = TfidfVectorizer(stop_words=stop_words,
                                     tokenizer=processing,
                                     ngram_range=(1, n))
    X = idf_vectorizer.fit_transform(corpus)
    y_values = df.Rating.astype("category")

    return X, y_values, idf_vectorizer


# -----------------------------------------------------------------------------
#   PREVIOUS ATTEMPT AT CALCULATING TFIDF SCORE WITHOUT USING TFIDFVECTORIZER LIBRARY
#   MANAGED TO GET DESIRED OUTPUT BUT REQUIRES TOO MUCH COMPUTING POWER

# def make_ngrams(tokens, n):
#     '''
#     Take the list of words from a single review and create n-grams.

#     Input:
#       - text (list of str): list of processed words in a review
#       - n (int): maximum number of words per n-gram

#     Returns: list of 1- to n-word strings for a single review
#     '''
#     ngrams = []

#     for i in range(1, n+1):
#         ngrams += [" ".join(tuple(tokens[j:j+i]))
#                    for j in range(len(tokens) - i + 1)]

#     return ngrams


# Processing Stage
# def count_tokens(tokens):
#     '''
#     Count each distinct token (entity) in a list of tokens.

#     Inputs:
#       - tokens (list of str): list of tokens

#     Returns: dict mapping tokens to counts
#     '''
#     rv = {}

#     for tok in tokens:
#         rv[tok] = rv.get(tok, 0) + 1

#     return rv


# def compute_idf(docs):
#     '''
#     Calculate the inverse document frequency (idf) for each
#     token in a collection of documents (D), where
#         idf(t, D) = log(total number of documents in D /
#                         number of documents containing t).

#     Inputs:
#       - docs (list of list of str): list of lists of tokens

#     Returns: dict mapping terms to idf values
#     '''
#     num_docs = len(docs)

#     idf_dict = {}
#     docs_set = [set(doc) for doc in docs]
#     tokens = set.union(*docs_set)

#     for token in tokens:
#         docs_with_token = sum([1 for doc in docs_set
#                                if (token in doc)])
#         idf_dict[token] = math.log(num_docs / docs_with_token)

#     return idf_dict


# Vectorizing Stage
# def tfidf_vectorize(revs):
#     '''
#     Calculate the tf_idf for each term per document in a collection
#     of documents. By definition,
#         tf = 0.5 + 0.5 * (freq_of_term_in_doc / max_freq_in_doc)
#     and
#         tf_idf = tf * idf.

#     Inputs:
#       - list of lists of strings (list of str): collection of reviews

#     Returns: DataFrame (tf_idf) and dict (idf)
#     '''
#     token_to_freq_by_rev = [count_tokens(rev) for rev in revs]
#     idf = compute_idf(revs)

#     for rev in token_to_freq_by_rev:
#         max_freq = max(rev.values())
#         for token in rev:
#             tf = 0.5 + 0.5 * (rev[token] / max_freq)
#             rev[token] = tf * idf[token]

#     return pd.DataFrame(token_to_freq_by_rev).fillna(0), idf


# def get_df_idf_stops(csv_file, n=2, lemmatized=True,
#                      num_stop_words=20):
#     '''
#     Given a dataframe with two columns, Rating and Text,
#     returns a dataframe that vectorizes the text and joins it
#     back with the Rating column.
#     Given a dataframe with two columns, rating and text, generate a
#     dataframe that vectorizes the text, and join it back with the
#     rating column.
#     Inputs:
#         csv_file (csv): csv file containing scraped reviews from Yelp
#         csv_file (str): CSV file containing scraped Yelp reviews
#         n (int): range of n-grams to use
#         remove_stop (boolean): True if stop words need to be removed
#         lemmatized (bool): whether or not to lemmatize words
#         num_stop_words (int): number of stop words to remove
#     Returns:
#         final dataframe for modelling
#     Returns: DataFrame, dict (idf), and list (stop words)
#     '''

#     df = pd.read_csv(csv_file, usecols=[0, 1],
#                      names=["Rating", "Text"], header=None)
#     all_tokens = [processing(text, lemmatized) for text in df.Text]

#     if num_stop_words > 0:
#         stop_words = get_stop_words(all_tokens, num_stop_words)
#         all_tokens = [[token for token in tokens if token not in stop_words]
#                       for tokens in all_tokens]

#     ngrams = [make_ngrams(tokens, n) for tokens in all_tokens]

#     final_df, idf = tfidf_vectorize(ngrams)
#     y_values = df.Rating.astype('category')
#     y_values = df.Rating.astype("category")

#     final_df["Rating"] = y_values

#     if num_stop_words > 0:
#         return final_df, idf, stop_words
#     else:
#         return final_df, idf, []
