import pandas as pd
import numpy as np
import joblib
import json
import itertools
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import classification_report
from analyze_words import get_df_idf_stops


def evaluateModel(prediction, y_test):
    '''
    Calculate the accuracy of a model based on the proportion of
    accurate predictions using the testing data. Accuracy is
    weighted by the deviance from the actual rating.

    Inputs:
      - prediction (arr): predicted y values
      - y_test (arr): actual y values

    Returns: float
    '''
    # Convert into DataFrame for easier handling
    pred_test_df = pd.DataFrame({"predict": prediction,
                                 "actual": y_test}).astype("int")
    pred_test_df["difference"] = (pred_test_df.predict
                                  - pred_test_df.actual).abs()

    num_tests = len(pred_test_df.index)
    total_deviance = pred_test_df["difference"].sum()

    # Maximum deviance is 4 (5-star rating vs. 1-star rating)
    weighted_accuracy = 1 - (total_deviance / (4 * num_tests))

    return weighted_accuracy


def get_weighted_accuracy(x_train, x_test, y_train, y_test, alpha):
    '''
    Calculate weighted accuracy of a model.

    Inputs:
      - x_train (DataFrame): x training data
      - x_test (DataFrame): x testing data
      - y_train (arr): y training data
      - y_test (arr): y testing data
      - alpha (float): constant that multiplies regularization term

    Returns: float
    '''
    model = linear_model.SGDClassifier(alpha=alpha)
    trained_model = model.fit(x_train, y_train)
    prediction = trained_model.predict(x_test)
    weighted_accuracy = evaluateModel(prediction, y_test)

    return weighted_accuracy


def feature_selection(model, x_train, y_train, x_test, column_names):
    '''
    Performs feature selection to minimize overfitting

    Inputs:
        - model (Model): model being applied
        - x_train (DataFrame): x training data
        - y_train (arr): y training data
        - x_test (DataFrame): x testing data
        - column_names (Series): original column names

    Returns: 3 arrs (filtered x_train, filtered x_test, filtered column names)
    '''
    trained_model = model.fit(x_train, y_train)
    feature_selection_model = SelectFromModel(trained_model)
    trained_feature_selection_model = feature_selection_model.fit(x_train,
                                                                  y_train)
    x_train = trained_feature_selection_model.transform(x_train)
    x_test = trained_feature_selection_model.transform(x_test)

    feature_idx = trained_feature_selection_model.get_support()
    column_names = column_names[feature_idx]

    return x_train, x_test, column_names


def optimize_model(csv_file, testing_fraction=0.95):
    '''
    Find the optimal combination of parameters (maximum n-gram length,
    whether to lemmatize, number of stop words, and alpha) for the
    suggested star rating model, as well as the corresponding DataFrame, 
    idf dictionary, and list of stop words.

    Inputs:
      - csv_file (string): CSV file name
      - testing_fraction (float): proportion of data reserved for testing

    Returns: DataFrame, dict (parameters), dict (idf), list of str
    '''
    # Combinations
    ngrams = [1, 2, 3]
    lemmatizes = [True, False]
    num_stop_words = [0, 10, 20]
    alphas = [0.0001, 0.001, 0.01, 0.1, 1]

    all_combi = list(itertools.product(ngrams, lemmatizes,
                                       num_stop_words, alphas))

    max_accuracy = -1
    best_combi = None
    best_idf = None
    best_df = None
    best_stop_words = None

    print("Completed initializing.")

    for combi in all_combi:
        ngram, lemmatize, num_stop_words, alpha = combi
        df, idf, stop_words = get_df_idf_stops(csv_file, n=ngram,
                                               lemmatized=lemmatize,
                                               num_stop_words=num_stop_words)
        x_train, x_test, y_train, y_test = \
            train_test_split(df.drop("Rating", axis=1), df.Rating,
                             test_size=testing_fraction, random_state=33)
        weighted_accuracy = get_weighted_accuracy(x_train, x_test,
                                                  y_train, y_test, alpha)

        print(combi, "Finished testing. | Accuracy: ", weighted_accuracy)

        if weighted_accuracy > max_accuracy:
            max_accuracy = weighted_accuracy
            best_combi = combi
            best_idf = idf
            best_df = df
            best_stop_words = stop_words

    best_combi_dict = {"ngram": best_combi[0], "lemmatize": best_combi[1],
                       "num_stop_words": best_combi[2], "alpha": best_combi[3]}

    return best_df, best_combi_dict, best_idf, best_stop_words


def main_modelling(csv_file, testing_fraction=0.2):
    '''
    Generate the optimal model for predicting Yelp review ratings by
    cycling through combinations of parameters and save it as a PKL file.
    Also saves other parameters for user input processing in JSON files.

    Inputs:
      - csv_file (string): CSV file name
      - testing_fraction (float): proportion of data reserved for testing

    Returns: None, writes PKL and JSON files
    '''
    # Input and Model Tuning
    df, combi, idf, stop_words = optimize_model(csv_file, testing_fraction)

    x_train, x_test, y_train, y_test = \
        train_test_split(df.drop("Rating", axis=1), df.Rating,
                         test_size=testing_fraction, random_state=33)

    # Feature Selection
    model = linear_model.SGDClassifier(alpha=combi["alpha"])
    x_train, x_test, column_names = feature_selection(model, x_train,
                                                      y_train, x_test,
                                                      df.drop("Rating",
                                                              axis=1).columns)
    final_model = model.fit(x_train, y_train)
    prediction = final_model.predict(x_test)

    print("Final Model Classification Report")
    print(classification_report(prediction, y_test))
    print("Accuracy Score")
    print(evaluateModel(prediction, y_test))

    # Save best Model
    joblib.dump(final_model, "optimal_args/final_model.pkl")

    # Save best columns, idf, combination, and stop words
    with open("optimal_args/columns.json", "w") as f:
        json.dump(list(column_names), f)
    with open("optimal_args/idf.json", "w") as f:
        json.dump(idf, f)
    with open("optimal_args/combination.json", "w") as f:
        json.dump(combi, f)
    with open("optimal_args/num_stop_words.json", "w") as f:
        json.dump(stop_words, f)
