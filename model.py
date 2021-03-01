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


def applyModels(model, x_train, y_train):
    print(model)
    model.fit(x_train, y_train)
    return model


def predictModel(model, x_test):
    prediction = model.predict(x_test)
    return prediction


def evaluateModel(model, prediction, x, y):
    start_time = time.time()
    confusion = confusion_matrix(y.to_numpy(), prediction)
    accuracy = accuracy_score(y, prediction)*100
    f1 = f1_score(y, prediction, average='macro')
    cr = classification_report(prediction, y)
    completed_time = time.time() - start_time
    print('Evaluation Time: ', completed_time)
    return {
        'prediction': prediction,
        'confusion': confusion,
        'accuracy': accuracy,
        'classification report': cr,
        'f1': f1
    }


def generate_additional_features():
    # in case we want to include number of taggings (like verb, noun) to our columns
    pass


def select_features():
    # implement feature selection algorithm,
    # this is similar to the forward selection/greedy algorithm we did in PA5 Fall Quarter
    pass


def main(df, testing_fraction=0.2):
    # Potential for nested for loops here to manipulate n and remove stop and number of stop words
    df, idf = get_final_df(csv_file)
    x_train, x_validate_test, y_train, y_validate_test = train_test_split(df.drop("Rating", axis=1),
                                                                          df.Rating,
                                                                          test_size=testing_fraction,
                                                                          random_state=33)
    x_validate, x_test, y_validate, y_test = train_test_split(x_validate_test,
                                                              y_validate_test,
                                                              test_size=0.5,
                                                              random_state=33)
    # Potential for loops to manipulate model parameters
    model = linear_model.SGDClassifier(loss='hinge', alpha=0.0001, penalty='l2',
                                       max_iter=300, tol=None, shuffle=True)
    trained_model = applyModels(model, x_train, y_train)
    prediction = predictModel(trained_model, x_test)
    result = evaluateModel(trained_model, prediction, x_test, y_test)

    print(result)

    # Saves Model
    joblib.dump(trained_model, "perfect_model.pkl")
