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


def applyModels(model, x_train, y_train):
    model.fit(x_train, y_train)
    return model


def predictModel(model, x_test):
    prediction = model.predict(x_test)
    return prediction


def evaluateModel(prediction, y_test):
    '''
    Calculate the accuracy of model based on the proportion of accurate 
    predictions using the testing data. Calculation is weighted by the degree of
    deviance from 'actual rating'.
    '''
    # convert into pandas dataframe for easier handling
    pred_test_df = pd.DataFrame({'predict': prediction,
                                 'actual': y_test}).astype('int')
    pred_test_df['difference'] = (pred_test_df.predict -
                                  pred_test_df.actual).abs()

    num_tests = len(pred_test_df.index)
    total_deviance = pred_test_df['difference'].sum()

    # maximum deviance is 4 (5 star rating vs 1 star rating)
    weighted_accuracy = 1 - (total_deviance / (4 * num_tests))

    return weighted_accuracy


def transformFeatureSelection(model, x):
    return model.transform(x)


def applyFeatureSelection(model, x_train, y_train):
    model = model.fit(x_train, y_train)
    return model


def generate_additional_features():
    # in case we want to include number of taggings (like verb, noun) to our columns
    pass


def tune_inputs(csv_file, testing_fraction=0.2):
    # Combinations
    ngrams = [1, 2, 3, 4, 5]
    lemmatizes = [True, False]
    stop_words = [0, 10, 20]
    alphas = [0.0001, 0.001, 0.01, 0.1, 1]

    max_accuracy = -1
    best_comb = {}
    best_idf = None
    best_df = None
    best_stop = None

    for ngram in ngrams:
        for lemmatize in lemmatizes:
            for stop_word in stop_words:
                for alpha in alphas:
                    df, idf, chosen_stops = get_final_df(csv_file, n=ngram,
                                                         lemmatized=lemmatize,
                                                         num_stop_words=stop_word)
                    x_train, x_test, y_train, y_test = train_test_split(df.drop("Rating", axis=1),
                                                                        df.Rating,
                                                                        test_size=testing_fraction,
                                                                        random_state=33)

                    model = linear_model.SGDClassifier(alpha=alpha)
                    trained_model = applyModels(model, x_train, y_train)
                    prediction = predictModel(trained_model, x_test)
                    accuracy = evaluateModel(prediction, y_test)

                    if accuracy > max_accuracy:
                        max_accuracy = accuracy
                        best_comb["ngram"] = ngram
                        best_comb["lemmatize"] = lemmatize
                        best_comb["stop_word"] = stop_word
                        best_comb["alpha"] = alpha
                        best_idf = idf
                        best_df = df
                        best_stop = chosen_stops

    return best_df, best_comb, best_idf, best_stop


def main_modelling(csv_file, testing_fraction=0.2):
    # Input and Model Tuning
    df, comb, idf, stop = tune_inputs(csv_file, testing_fraction)

    x_train, x_test, y_train, y_test = train_test_split(df.drop("Rating", axis=1),
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
    joblib.dump(final_model, "final_model.pkl")

    # Save best columns, idf, combination, and stop words
    feature_idx = trained_feature_selection_model.get_support()
    column_names = df.drop("Rating", axis=1).columns[feature_idx]
    with open('columns.json', 'w') as f:
        json.dump(list(column_names), f)
    with open('idf.json', 'w') as f:
        json.dump(idf, f)
    with open('combination.json', 'w') as f:
        json.dump(comb, f)
    with open('stop_words.json', 'w') as f:
        json.dump(stop, f)
