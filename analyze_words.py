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
import nltk
# nltk.download('wordnet')


STOP_PREFIXES = ("@", "#", "http", "&amp")


def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P')


PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])


def processing(text):
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


def get_stop_words(all_tokens):
    '''
    Inputs:
        - all_tokens (list of list of strings): a list of list of all tokens

    Returns:
        - list of 10 most common words
    '''
    all_words = list(itertools.chain.from_iterable(all_tokens))
    freq_dist = FreqDist(all_words)
    stop_words = freq_dist.most_common(10)

    return [word[0] for word in stop_words]


def remove_stop(stop_words, tokens):
    '''
    Takes the list of words from a single review and removes
    generated stop words

    Input:
        text (list of str): list of processed words in a review

    Returns:
        list of string representing words in a single review
    '''

    return [token for token in tokens if token not in stop_words]


def make_ngrams(tokens, n):
    '''
    Takes the list of words from a single review and create n-grams

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
    Counts each distinct token (entity) in a list of tokens.

    Inputs:
        tokens: list of tokens (must be immutable)

    Returns: dictionary that maps tokens to counts
    '''
    rv = {}
    for tok in tokens:
        # Initialize entry if unseen; always increment count
        rv[tok] = rv.get(tok, 0) + 1

    return rv


def compute_idf(docs):
    '''
    Calculate the inverse document frequency (idf) for each term (t) in a
    collection of documents (D). By definition,
      idf(t, D) = log(total number of documents in D / number of documents
                      containing t).
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


def augmented_freq(doc):
    '''
    Compute the augmented term frequency values of the tokens in a document

    Inputs: 
        doc: a list of tokens

    Returns: dictionary that maps terms to their augmented frequency
    '''

    token_dict = count_tokens(doc)
    tf_dict = {}
    max_count = max(token_dict.values())

    for token, count in token_dict.items():
        tf_dict[token] = 0.5 + 0.5 * (count / max_count)

    return tf_dict


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
    In:
      - list of lists of strings, e.g., [["i", "love", "food"],
                                         ["i", "hate", "food"]]

    Out: pandas DataFrame, e.g.,      i  love  food  hate
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

    return pd.DataFrame(tok_to_freq_by_rev).fillna(0)


def get_final_df(csv_file, n, stop_removed):
    '''
    Given a dataframe with two columns, Rating and Text, 
    returns a dataframe that vectorizes the text and joins it
    back with the Rating column.

    Inputs: 
        df (pd df): the dataframe
        n (int): range of n-grams to use
        stop_removed (boolean): True if stop words need to be removed

    Returns: 
        final dataframe for modelling
    '''

    df = pd.read_csv(csv_file)
    all_tokens = [processing(text) for text in df.Text]

    if stop_removed:
        stop_words = get_stop_words(all_tokens)
        all_tokens = [remove_stop(stop_words, tokens) for tokens in all_tokens]

    ngrams = [make_ngrams(tokens, n) for tokens in all_tokens]

    final_df = tfidf_vectorize(ngrams)
    y_values = df.Rating.astype('category')

    final_df.insert(0, "Rating", y_values)

    return final_df


# TESTING
get_final_df("./test_data/babareba.csv", 2, False)
