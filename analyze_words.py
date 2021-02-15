import csv
import pandas as pd

STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with"]

# When processing tweets, words w/ a prefix that appears in this list
# should be ignored.
STOP_PREFIXES = ("@", "#", "http", "&amp")

data = pd.read_csv("./test_data/babareba.csv")
df = pd.DataFrame(data, columns = ['Rating', 'Text'])
print(df)

#df[reviews].apply()

def processing(df):
    #this is def wrong need to fix, need to be able to iterate through the paragraph of the review itself
    review = df.loc[:, "Text"]
    print(review)
    processed_review = []
    split_review = review.split()
    for word in split_review:
        word = i.strip(PUNCTUATION)
        word = word.lower()
        if word not in set(STOP_WORDS) and not word.startswith(STOP_PREFIXES) and len(word) > 0:
            processed_review.append(word)
    return processed_review

#def parse_words():
    #pass


