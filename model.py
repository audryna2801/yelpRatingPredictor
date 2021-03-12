import pandas as pd
import numpy as np
import joblib
import itertools
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import classification_report
from analyze_words import get_df_idf_stops


RANDOM_SEED = 33


def evaluate_model(prediction, y_test):
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

    num_tests = len(pred_test_df)
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
    weighted_accuracy = evaluate_model(prediction, y_test)

    return weighted_accuracy


def feature_selection(model, x_train, y_train, x_test):
    '''
    Perform feature selection to minimize overfitting.

    Inputs:
        - model (Model): model being applied
        - x_train (DataFrame): x training data
        - y_train (arr): y training data
        - x_test (DataFrame): x testing data

    Returns: 2 arrs (filtered x_train, filtered x_test), 
             Selector obj (trained_feature_selection_model)
    '''
    trained_model = model.fit(x_train, y_train)
    feature_selection_model = SelectFromModel(trained_model)
    trained_feature_selection_model = feature_selection_model.fit(x_train,
                                                                  y_train)
    x_train = trained_feature_selection_model.transform(x_train)
    x_test = trained_feature_selection_model.transform(x_test)

    return x_train, x_test, trained_feature_selection_model


def optimize_model(csv_file, testing_fraction):
    '''
    Find the optimal combination of parameters (maximum n-gram length,
    number of stop words, and alpha) for the suggested star rating model, 
    as well as the corresponding x and y values, and vectorizer object.

    Inputs:
      - csv_file (string): CSV file name
      - testing_fraction (float): proportion of data reserved for testing

    Returns: list of array (best_x), series (best_y), int (best_alpha), 
             Vectorizer obj (best_vectorizer)
    '''
    # Combinations
    ngrams = [1, 2, 3]
    num_stop_words = [0, 10, 20]
    alphas = [0.0001, 0.001, 0.01, 0.1, 1]

    all_combi = list(itertools.product(ngrams, num_stop_words, alphas))

    max_accuracy = -1
    best_x = None
    best_y = None
    best_alpha = None
    best_vectorizer = None

    print("Completed initializing.")

    for combi in all_combi:
        ngram, num_stop_words, alpha = combi
        X, y_values, vectorizer = get_df_idf_stops(csv_file, n=ngram,
                                                   num_stop_words=num_stop_words)
        x_train, x_test, y_train, y_test = \
            train_test_split(X, y_values, test_size=testing_fraction,
                             random_state=RANDOM_SEED)
        weighted_accuracy = get_weighted_accuracy(x_train, x_test,
                                                  y_train, y_test, alpha)

        print(combi, "Finished testing. | Accuracy: ", weighted_accuracy)

        if weighted_accuracy > max_accuracy:
            max_accuracy = weighted_accuracy
            best_x = X
            best_y = y_values
            best_alpha = alpha
            best_vectorizer = vectorizer

    return best_x, best_y, best_alpha, best_vectorizer


def main_modelling(csv_file="test_data/merged_data.csv", testing_fraction=0.2):
    '''
    Generate the optimal model for predicting Yelp review ratings by
    cycling through combinations of parameters and saving it as a PKL file.
    Also saves the vectorizer and selector object for user input processing
    as PKL files.  

    Inputs:
      - csv_file (string): CSV file name
      - testing_fraction (float): proportion of data reserved for testing

    Returns: None, writes PKL files
    '''
    # Input and Model Tuning
    X, y_values, alpha, vectorizer = optimize_model(csv_file, testing_fraction)

    x_train, x_test, y_train, y_test = \
        train_test_split(X, y_values, test_size=testing_fraction,
                         random_state=RANDOM_SEED)

    # Feature Selection
    model = linear_model.SGDClassifier(alpha=alpha)
    x_train, x_test, feature_selector = feature_selection(model, x_train,
                                                          y_train, x_test)
    final_model = model.fit(x_train, y_train)
    prediction = final_model.predict(x_test)

    print("Final Model Classification Report")
    print(classification_report(prediction, y_test))
    print("Accuracy Score")
    print(evaluate_model(prediction, y_test))

    # Save best Model, Vectorizer, and Selector
    joblib.dump(final_model, "optimal_args/final_model.pkl")
    joblib.dump(vectorizer, "optimal_args/vectorizer.pkl")
    joblib.dump(feature_selector, "optimal_args/selector.pkl")
