import pandas as pd
import numpy as np
import time
import joblib
import json
from sklearn.svm import LinearSVC, SVC
from sklearn import linear_model, tree, neighbors
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import f1_score, accuracy_score
from sklearn import preprocessing
from nltk import pos_tag
from analyze_words import *
import itertools


def applyModels(model, x_train, y_train):
    '''
    Fit a model to a pair of x and y training data.

    Inputs:
      - model (Model): model being fitted
      - x_train (arr): x training data
      - y_train (arr): y training data

    Returns: Model
    '''
    model.fit(x_train, y_train)
    return model


def predictModel(model, x_test):
    '''
    Use a model to generate a prediction for y from x testing data.

    Inputs:
      - model (Model): model being applied
      - x_test (arr): x testing data

    Returns: arr
    '''
    prediction = model.predict(x_test)
    return prediction


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
    pred_test_df = pd.DataFrame({'predict': prediction,
                                 'actual': y_test}).astype('int')
    pred_test_df['difference'] = (pred_test_df.predict
                                  - pred_test_df.actual).abs()

    num_tests = len(pred_test_df.index)
    total_deviance = pred_test_df['difference'].sum()

    # Maximum deviance is 4 (5-star rating vs. 1-star rating)
    weighted_accuracy = 1 - (total_deviance / (4 * num_tests))

    return weighted_accuracy


def get_weighted_accuracy(x_train, x_test, y_train, y_test, alpha):
    '''
    Calculate weighted accuracy of a model.

    Inputs:
      - x_train (arr): x training data
      - x_test (arr): x testing data
      - y_train (arr): y training data
      - y_test (arr): y testing data
      - alpha (float): constant that multiplies regularization term

    Returns: float
    '''
    model = linear_model.SGDClassifier(alpha=alpha)
    trained_model = applyModels(model, x_train, y_train)
    prediction = predictModel(trained_model, x_test)
    weighted_accuracy = evaluateModel(prediction, y_test)

    return weighted_accuracy


def transformFeatureSelection(model, x):
    # Need doc string
    return model.transform(x)


def applyFeatureSelection(model, x_train, y_train):
    # Need doc string
    model = model.fit(x_train, y_train)
    return model


def generate_additional_features():
    # In case we want to include number of taggings
    # (like verb, noun) to our columns
    pass


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

    all_combi = list(itertools.product(
        ngrams, lemmatizes, num_stop_words, alphas))

    max_accuracy = -1
    best_combi = None
    best_idf = None
    best_df = None
    best_stop = None

    print("Completed initializing.")

    for combi in all_combi:
        ngram, lemmatize, num_stop_words, alpha = combi
        df, idf, chosen_stops = get_df_idf_stops(csv_file, n=ngram,
                                                 lemmatized=lemmatize,
                                                 num_stop_words=num_stop_words)
        (x_train, x_test,
         y_train, y_test) = train_test_split(df.drop("Rating", axis=1),
                                             df.Rating,
                                             test_size=testing_fraction,
                                             random_state=33)
        weighted_accuracy = get_weighted_accuracy(x_train, x_test,
                                                  y_train, y_test, alpha)

        print(combi, "Finished testing. | Accuracy: ", weighted_accuracy)

        if weighted_accuracy > max_accuracy:
            max_accuracy = weighted_accuracy
            best_combi = combi
            best_idf = idf
            best_df = df
            best_stop = chosen_stops

    best_combi_dict = {"ngram": best_combi[0], "lemmatize": best_combi[1],
                       "num_stop_words": best_combi[2], "alpha": best_combi[3]}

    return best_df, best_combi_dict, best_idf, best_stop


def main_modelling(csv_file, testing_fraction=0.95):
    '''
    Generate the optimal model for predicting Yelp review ratings by
    cycling through combinations of parameters and save it as a PKL file.

    Inputs:
      - csv_file (string): CSV file name
      - testing_fraction (float): proportion of data reserved for testing

    Returns: None, writes PKL file
    '''
    # Input and Model Tuning
    df, comb, idf, stop = optimize_model(csv_file, testing_fraction)

    (x_train, x_test,
     y_train, y_test) = train_test_split(df.drop("Rating", axis=1),
                                         df.Rating,
                                         test_size=testing_fraction,
                                         random_state=33)

    # Feature Selection
    model = linear_model.SGDClassifier(alpha=comb["alpha"])
    trained_model = applyModels(model, x_train, y_train)
    feature_selection_model = SelectFromModel(trained_model)
    trained_feature_selection_model = applyFeatureSelection(feature_selection_model,
                                                            x_train, y_train)
    x_train = transformFeatureSelection(trained_feature_selection_model,
                                        x_train)
    x_test = transformFeatureSelection(trained_feature_selection_model,
                                       x_test)

    final_model = applyModels(model, x_train, y_train)
    prediction = predictModel(final_model, x_test)

    print("Final Model Classification Report")
    print(classification_report(prediction, y_test))
    print("Accuracy Score")
    print(evaluateModel(prediction, y_test))

    # Save best Model
    joblib.dump(final_model, "optimal_args/final_model.pkl")

    # Save best columns, idf, combination, and stop words
    feature_idx = trained_feature_selection_model.get_support()
    column_names = df.drop("Rating", axis=1).columns[feature_idx]
    with open('optimal_args/columns.json', 'w') as f:
        json.dump(list(column_names), f)
    with open('optimal_args/idf.json', 'w') as f:
        json.dump(idf, f)
    with open('optimal_args/combination.json', 'w') as f:
        json.dump(comb, f)
    with open('optimal_args/num_stop_words.json', 'w') as f:
        json.dump(stop, f)
