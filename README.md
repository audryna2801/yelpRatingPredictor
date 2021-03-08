# The Yelp Rating Predictor

Hello and welcome to our final CMSC 12200 project: "The Yelp Rating Predictor"!

Our goal for this project was to create a program that predicts a Yelp rating (out of 5 stars) for a review using the Linear SVM model. First, we will be going into what each file does and how it contributes to the overarching goal of the project. Then, a short introduction on how to use the program. And lastly, we will evaluate the scope of what our project can do and the limitations that come with it. 

## Running the model

Make sure you have all of the libraries downloaded. In the terminal, run "python3 main.py". Type in your review and press enter to get the star rating.

## Files

### crawl_and_scrape.py
This file was created to scrape the data neccessary for training our model. Using Beautiful Soup, this takes the Yelp landing page for Chicago restaurants and for every restaurant, scrapes all of the reviews into a csv file. It continues to do this for all of the restaurants in Chicago. One feature of this file, more specifcally of the function "get_reviews_from_page", contains the element of "sleeping" and a user-defined counter. Yelp attempts to block any attempts for web-scraping thus, making it hard for an algorithm to go through the web pages without being blocked. With this caveat in mind, we inputed a feature such that during scraping, it would randomly "sleep" to bypass the Yelp's detection system and/or tries again "counter" many times before giving up. This ended up working. We were able to get way more reviews scraped than before, however at the cost of a large runtime due to the random "sleeps" and more retries. 
### merge_data.py
This file contains one function that combines all restaurant reviews into one dataframe. Then, it grouped each review by rating and randomly sampled 2,000 reviews from each group. Header argument is determined if there is header column in each CSV file from scraped data. It outputs a dataframe with equal distribution of ratings. 
### analyze_words.py
This file focused on digesting the csv file that contains the 10,000 balanced reviews (output of merged_data.py) and outputting a dataframe with the corpus' tokens as the columns and the tfidf values for each review as the rows. It considers the  n-gram length, whether or not to lemmatize words, and how many stop words should be removed. 

Taking a csv file, we processed all of the words in it (stripping puncuation, lemmatization) and created tokens. Then, we get the stop words from the file by ranking the words by the highest frequency at which they appear and removed the top-n stop words (as indicated by the num_stop_words parameter) from each review's token list. Based on the specified n-gram number, we created n-gram ranges out of the tokens (ie. if a phrase was "the food is good", an n-gram of 2 would consist of "the", "food", is", "good", "the food", "food is", "is good"). Then, we computed the tfdif row of each review. We combined these steps together in "get_df_idf_stops" to compute a df that has the words passed through 3 arguments: the number of n-grams, if there is lemmatization or not, and number of stop_words.
### model.py
This file trains, test, and saves our model. We calculated a weighted accuracy and use feature selection to get the best model possible. The weighted accuracy method allows us to put more weight for far-off errors (i.e. predicting a 5 star review as a 1 star). The feature selection was done via sklearn library's feature selection function. It was done to reduce overfitting; given that our data comes from the Chicago area, we want to make our model flexible enough to also predict reviews from other locations accurately. Our function "main_modelling" generates the optimal model for predicting Yelp review ratings by cycling through combinations of parameters and saving it as a PKL file. It also saves other parameters necessary for user input processing in JSON files. Our optimize model function considers the parameters n-grams, lemmatization, number of stop words, and different variances of alphas to return the best model and input dataframe, before running feature selection on it. This reveals the model we will be using for our program.
### main.py
This file combines functions from analyze_words and model to complete our program's user interface. The user will be prompted by the UI to input their review and this will call on analyze_word's "processing" to turn the data into tokens. Using the best combination as indicated by model.py, this text input will be turned into an array that matches our model's "columns" and used our saved model to predict the appropriate star rating, before outputting it to the user.

## Folders

### iPython_Tests
This contains jupyter notebook used for testing. In order to test that our program was accurate, we tested against various amounts of ratios between training and testing data and found that our model was consistently successful, even when given a smaller amount of traning data. 
### optimal_args
This folder contains all of the optimal arguments for our final model, created by model.py and used in the main.py. 
### scraped_data
This contains all of the raw, scraped data from Yelp.
### test_data
This contains the data that we test on, aka what our merged_data.py creates. 


## Conclusion

### On optimizing the model
We optimized our model using the standard training-testing split 80-20 as well as a 5-95 split. Our best combination (ngram, lemmatize, num_stop_words, alpha) was: (1, False, 0, 0.001) for the first split and (1, False, 0, 0.1) for the second. The resulting combination was mostly similar, with the exception of the alpha parameter. This indicates that our optimizing function is more or less robust. 

### Downsides
Our program largely depends on wording, not sentiment. Humans are able to detect inflection and tone when reading whereas our program cannot. Because of the time constraints of this project, we were unable to implement a program that can detect sarcasm and therefore, sometimes mixes up reviews that were meant to be read ironically, as literally. However, when given a robust review of honest opinions and feelings towards a restaurant, our program is able to accurately predict the star rating most of the time. 