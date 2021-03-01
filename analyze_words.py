import nltk
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from nltk import FreqDist
import itertools
import csv
import re
import pandas as pd
import unicodedata
import sys
import math
nltk.download('wordnet')


STOP_PREFIXES = ("@", "#", "http", "&amp")


def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P')


PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])


def processing(text, stem=True):
    '''
    Converts a text of a review  into a list of strings

    Inputs:
        text (str): text representing one review

    Returns:
        list of words
    '''

    lemmatizer = WordNetLemmatizer()

    # Try to fix spelling errors before splitting
    # textBlb = TextBlob(text)
    # corrected_text = textBlb.correct()

    split_text = text.split()
    new_text = []

    for word in split_text:
        # Handles trailing and inner punctuations
        word = word.strip(PUNCTUATION)
        word = word.replace("&apos;", "'")
        word = word.replace('quot;', '"')
        word = word.replace('&quot', '"')

        word = word.lower()
        
        if stem:
            lemmatizer.lemmatize(word)

        # Splits words if / present
        if '/' in word:
            words = word.split('/')
            new_text += [word for word in words if not bool(
                re.search(r'\d', word)) and not word.startswith(STOP_PREFIXES)]
        else:
            if (word and not bool(re.search(r'\d', word))
                    and not word.startswith(STOP_PREFIXES)):
                new_text.append(word)

    return new_text


def get_stop_words(all_tokens, num_stop_words=20):
    '''
    Obtain the particular stop words (most frequently occurring words) in the
    sample, which may differ from a list of generic stop words.

    Inputs:
        - all_tokens (list of list of strings): a list of list of all tokens
        - num_stop_words (int): number of stop words to remove

    Returns:
        - list of most common words
    '''
    all_words = list(itertools.chain.from_iterable(all_tokens))
    freq_dist = FreqDist(all_words)
    stop_words = freq_dist.most_common(num_stop_words)

    return [word[0] for word in stop_words]

# not needed, used directly in get_final_df
# def remove_stop(stop_words, tokens):
#     '''
#     Take the list of words from a single review and remove
#     stop words.

#     Input:
#         text (list of str): list of processed words in a review

#     Returns:
#         list of string representing words in a single review
#     '''

#     return [token for token in tokens if token not in stop_words]


def make_ngrams(tokens, n):
    '''
    Take the list of words from a single review and create n-grams

    Input:
        text (list of str): list of processed words in a review
        n: the length of the words

    Returns: list of 1 to n words strings for a single review
    '''

    ngrams = []

    for i in range(1, n+1):
        ngrams += [' '.join(tuple(tokens[j:j+i]))
                   for j in range(len(tokens) - i + 1)]

    return ngrams


# Vectorizing Stage
def count_tokens(tokens):
    '''
    Count each distinct token (entity) in a list of tokens.

    Inputs:
        tokens: list of tokens (must be immutable)

    Returns: dictionary that maps tokens to counts
    '''
    rv = {}
    for tok in tokens:
        rv[tok] = rv.get(tok, 0) + 1

    return rv


def compute_idf(docs):
    '''
    Calculate the inverse document frequency (idf) for each term (t) in a
    collection of documents (D). 

    idf(t, D) = log(total number of documents in D / 
                    number of documents containing 't').

    Helper function for find_salient.

    Inputs:
        docs: list of lists of tokens

    Returns: dictionary that maps each term to its idf
    '''
    num_docs = len(docs)

    idf_dict = {}
    docs_set = [set(doc) for doc in docs]
    tokens = set.union(*docs_set)

    for token in tokens:
        docs_with_token = sum([1 for doc in docs_set if (token in doc)])
        idf_dict[token] = math.log(num_docs / docs_with_token)

    return idf_dict


SAMPLE_DOCS = [['i', 'love', 'food', 'so', 'much'],
               ['good', 'service'],
               ['i', 'hate', 'this', 'restaurant']]

# SAMPLE_OUTPUT:
#           i      love      food        so      much      good   service      hate      this  restaurant
# 0  0.405465  1.098612  1.098612  1.098612  1.098612       NaN       NaN       NaN       NaN         NaN
# 1       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612       NaN       NaN         NaN
# 2  0.405465       NaN       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612    1.098612


def tfidf_vectorize(revs):
    '''
    Calculate the tf_idf for each term per document in a collection of
    documents. By definiion,
        tf = 0.5 + 0.5 * (freq_of_term_in_doc / max_freq_in_doc)
    and
        tf_idf = tf * idf.

    In:
      - list of lists of strings, e.g., [["i", "love", "food"],
                                         ["i", "hate", "food"]]

    Returns: pandas DataFrame, e.g.,      i  love  food  hate
                                     0  0.5   0.5   0.5   0.0
                                     1  0.3   0.0   0.4   0.5
    '''
    tok_to_freq_by_rev = [count_tokens(rev) for rev in revs]
    idf = compute_idf(revs)

    for rev in tok_to_freq_by_rev:
        max_freq = max(rev.values())
        for tok in rev:
            tf = 0.5 + 0.5 * (rev[tok] / max_freq)
            rev[tok] = tf * idf[tok]

    return pd.DataFrame(tok_to_freq_by_rev).fillna(0), idf


def get_final_df(csv_file, n=3, remove_stop=True, num_stop_words=20):
    '''
    Given a dataframe with two columns, Rating and Text, 
    returns a dataframe that vectorizes the text and joins it
    back with the Rating column.

    Inputs: 
        csv_file (csv): csv file containing scraped reviews from Yelp
        n (int): range of n-grams to use
        remove_stop (boolean): True if stop words need to be removed
        num_stop_words (int): number of stop words to remove

    Returns: 
        final dataframe for modelling
    '''

    df = pd.read_csv(csv_file, usecols=[0, 1], names=[
                     'Rating', 'Text'], header=None)
    all_tokens = [processing(text) for text in df.Text]

    if remove_stop:
        stop_words = get_stop_words(all_tokens, num_stop_words)
        # print(stop_words)
        all_tokens = [[token for token in tokens if token not in stop_words]
                      for tokens in all_tokens]

    ngrams = [make_ngrams(tokens, n) for tokens in all_tokens]

    final_df, idf = tfidf_vectorize(ngrams)
    y_values = df.Rating.astype('category')

    final_df["Rating"] = y_values

    return final_df, idf


# TESTING
get_final_df("./test_data/babareba.csv", 2, False)
