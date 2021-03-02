import pandas as pd
import numpy as np
from sklearn.svm import LinearSVC, SVC
from sklearn import linear_model, tree, neighbors
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import f1_score, accuracy_score
from sklearn import preprocessing
from nltk import pos_tag
import time
from analyze_words import get_final_df
import joblib
from sklearn.feature_selection import SelectFromModel


def applyModels(model, x_train, y_train):
    print(model)
    model.fit(x_train, y_train)
    return model


def predictModel(model, x_test):
    prediction = model.predict(x_test)
    return prediction


def evaluateModel(prediction, y_test):
    # Write function to weight errors
    pass


def transformFeatureSelection(model, x):
    return model.transform(x)


def applyFeatureSelection(model, x_train, y_train):
    model = model.fit(x_train, y_train)
    return model


def generate_additional_features():
    # in case we want to include number of taggings (like verb, noun) to our columns
    pass


def select_features():
    # implement feature selection algorithm,
    # this is similar to the forward selection/greedy algorithm we did in PA5 Fall Quarter
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

    for ngram in ngrams:
        for lemmatize in lemmatizes:
            for stop_word in stop_words:
                for alpha in alphas:
                    df, idf = get_final_df(csv_file, n=ngram,
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

    return best_df, best_comb, best_idf


def main(csv_file, testing_fraction=0.2):
    # Input and Model Tuning
    df, comb, idf = tune_inputs(csv_file, testing_fraction)

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
    prediction = predictModel(trained_model, x_test)

    print("Final Model Classification Report")
    print(classification_report(prediction, y_test))
    print("Accuracy Score")
    print(evaluateModel(prediction, y_test))

    # Saves best Model, Combination, Idf, and Column Names
    joblib.dump(final_model, "perfect_model.pkl")
    columns = list(x_test.columns)

    # how to save columns,
