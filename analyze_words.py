import csv
import pandas as pd
import unicodedata
import sys

from nltk.stem import WordNetLemmatizer

STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with"]

def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    (except #, @, &) and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P') and \
        (ch not in ("#", "@", "&"))

PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

STOP_PREFIXES = ("@", "#", "http", "&amp")

data = pd.read_csv("./test_data/babareba.csv")
df = pd.DataFrame(data, columns = ['Rating', 'Text'])

#df[reviews].apply()

def processing(df):
    X_array = [] 
    lemmatizer = WordNetLemmatizer()
    for i, row in df.iterrows():
        processed_review = []
    #this is def wrong need to fix, need to be able to iterate through the paragraph of the review itself
        review = row["Text"]
        #print(review)
        split_review = review.split()
        for word in split_review:
            word = word.strip(PUNCTUATION)
            word = word.lower()
            lemmatizer.lemmatize(word)
            if word not in set(STOP_WORDS) and not word.startswith(STOP_PREFIXES) and len(word) > 0:
                processed_review.append(word)
        X_array.append(processed_review)
    print(X_array)

#def parse_words():
    #pass


