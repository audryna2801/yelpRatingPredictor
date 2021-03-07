# The Yelp Rating Predictor

Hello and welcome to our final CMSC 12200 project: "The Yelp Rating Predictor"!

Our goal for this project was to create a program that predicts a Yelp rating (out of 5 stars) for a review using the Linear SVM model. First, we will be going into what each file does and how it contributes to the overarching goal of the project. Then, a short introduction on how to use the program. And lastly, we will evaluate the scope of what our project can do and the limitations that come with it. 

## Files

### crawl_and_scrape.py
This file was created to scrape the data neccessary for training our model. Using Beautiful Soup, this takes the Yelp landing page for Chicago restaurants and for every restaurant, scrapes all of the reviews into a csv file. It continues to do this for all of the restaurants in Chicago. One feature of this file, more specifcally of the function "get_reviews_from_page", contains the element of "sleeping". Yelp attempts to block any attempts for web-scraping thus, making it hard for an algorithm to go through the web pages without being blocked. With this caveat in mind, we inputed a fearture such that during scraping, it would randomly "sleep" to bypass the Yelp's detection system. This ended up working. We were able to get way more reviews scraped than before, however at the cost of a large runtime due to the random "sleeps". 
### analyze_words.py
This file focused on digesting the review csv and outputting a df considering n-gram length with all of the words, tokenized. This file mainly utilized the nltk library. Taking a csv file, we process all of the words in it (stripping puncuation, lemmatization). Then, we get the stop words from the file by ranking the words by the highest frequency at which they appear. With a n-gram number, we also create the n-grams for the words (ie. if a phrase was "the food is good", an n-gram of 2 would consist of "the food", "food is", "is good"). We also compute the idf and tfdif. Finally, we put these features together in "get_df_idf_stops" to compute a df that has the words passed through 3 arguments: the number of n-grams, if there is lemmatization or not, and number of stop_words.
### merge_data.py
This file contains one function that combines all restaurant reviews into one dataframe. Then, it group each review by rating and randomly sample 2,000 reviews from each group. Header argument is determined if there is header column in each CSV file from scraped data. It outputs a dataframe with equal distribution of ratings. 
### model.py
This file creates our model. We calculate a weighted accuracy and use feature selection to get the best model possible. Our function "main_modelling generate the optimal model for predicting Yelp review ratings by cycling through combinations of parameters and save it as a PKL file. Also saves other parameters for user input processing in JSON files. Our optimize model function considers the parameters n-grams, lemmization, number of stop words, and different variances of alphas to return the best dataframe, best combination, best idf, and best stop words. This reveals the model we will be using for our program.
### main.py
This file combines features from analyze_words and model to complete our program's user interface. The user will be prompted by thr UI to input their review and this will call on analyze_word's "processing" to turn the data into tokens. Using the best combination, this text input will be turned into an array in which it will be compared with the best model and then, output a star rating between 1-5.
### iPython_Tests
This contains jupyter notebook used for testing. In order to test that our program was accurate, we tested against various amounts of ratios between training and testing data and found that our model was consistently successful, even when given a smaller amount of traning data. 
### optimal_args
This folder contains all of the optimal arguments for our final model, used in the main.py. 
### scraped_data
This contains all of the raw, scraped data from Yelp.
### test_data
This contains the data that we test on, aka what our merged_data.py creates. 

## Running the model

Make sure you have all of the libraries downloaded. In the terminal, run "python3 main.py". Type in your review and press enter to get the star rating.

## Conclusion

### On optimizing the model


### Downsides
Our program largely depends on wording, not sentiment. Humans are able to detect inflection and tone when reading whereas our program cannot. Because of the time constraints of this project, we were unable to implement a program that can detect sarcasm and therefore, sometimes mixes up reviews that were meant to be read ironically, as literally. However, when given a robust review of honest opinions and feelings towards a restaurant, our program is able to accurately predict the star rating most of the time. 