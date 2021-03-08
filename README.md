# THE YELP RATING PREDICTOR

Hello and welcome to our final CMSC 12200 project: "The Yelp Rating Predictor"!

Our goal for this project was to create a program that predicts a Yelp rating (out of 5 stars) for a review using the Linear SVM model. First, we have a a short introduction on how to use the program. Then, we will be going into what each file does and how it contributes to the overarching goal of the project. Lastly, we will evaluate the scope of what our project can do and the limitations that come with it. 

## RUNNING THE PROGRAM

Make sure you have all of the libraries downloaded. In the terminal, run "python3 main.py". Type in your review and press enter to get the star rating.

## FILES

### crawl_and_scrape.py
This file was created to scrape the data neccessary for training our model. Using Beautiful Soup, this takes the Yelp landing page for Chicago restaurants and scrapes the URL for every restaurant in the city landing page. Then for every restaurant, it scrapes all of the reviews into a csv file. (EXPLANATION FOR WHY WE'RE SEPERATING ONE CSV FOR ONE RESTAURANT INSTEAD OF DOING IT ALL TOGETHER). One feature of this file, contains the element of "sleeping" and a user-defined counter (where a higher number corresponds to a longer run-time but fewer pages skipped). Yelp attempts to block attempts for web-scraping, making it hard for an algorithm to go through the web pages without being blocked. With this caveat in mind, we inputed a feature such that during scraping, for each page, it would randomly "sleep" to try to bypass the Yelp's detection system and/or tries again "counter" many times if it fails, before giving up and skipping the page. This ended up working as we were able to get way more reviews scraped than before. However this comes at the cost of a longer runtime due to the random "sleeps" and more retries. 
### merge_data.py
This file contains one function that combines all restaurant reviews scraped using the functions in crawl_and_scrape.py into one DataFrame. Then, it grouped each review by rating and randomly sampled 2,000 reviews from each group. It outputs a DataFrame of reviews with equal distribution of ratings. 
### analyze_words.py
This file focused on processing the csv file that contains the 10,000 balanced reviews (output of merged_data.py) and outputting a DataFrame with the corpus' tokens as the columns and the tfidf values for each review as the rows. It considers the n-gram length, whether or not to lemmatize words, and how many stop words should be removed. 

Taking the csv file, we processed each review (stripping punctuations or special characters, lemmatization, etc.) and created a list of tokens for each review. Then, we generated stop words by ranking the words by frequency (from the most to least frequent) and took the top-n words (as indicated by the num_stop_words parameter) as our stop_words. We didn't use default stop words library that is available because we thought that the most frequent words in restaurant reviews could potentially be different from other texts more generally. Then, we removed these chosen stop words from each review's token list. 

Based on the specified n-gram number, we created n-gram ranges out of the tokens (ie. if a phrase was "the food is good", an n-gram range of 2 would consist of "the", "food", is", "good", "the food", "food is", "is good"). Then, we computed the tfdif values of each token in each review. We combined these steps together in the function "get_df_idf_stops" to create the final DataFrame according to 3 parameters: the number of n-grams, if there is lemmatization or not, and the number of stop_words to remove.
### model.py
This file trains, test, and saves our model. To evaluate the accuracy of each model, we calculated a weighted accuracy that allows us to put more weight to far-off errors (i.e. predicting a 5 star review as a 1 star). In the function "optimize_model", we cycled through combination of parameters, namely: n-grams, lemmatization, number of stop words, and different variances of alphas to get the best combination that maximizes the accuracy of our model. Then, we used the output of this function in our "main_modelling" function where we further optimized the model by performing feature selection. The feature selection was done mainly using sklearn library's feature selection method. Although feature selection reduced our accuracy a little bit since it reduces the number of predictors in our model, it reduces the potential for overfitting. Given that our data comes exclusively from the Chicago area, reducing overfitting is important to make our model more robust in predicting reviews from other locations accurately. 

Then, "main_modelling" (after optimizing and feature selection) will save the best model as a PKL file, which is the model that we will use to predict user's review input. It also saves other parameters necessary for user input processing in JSON files, namely the idf dictionary, the best combination of parameters, and the list of stop_words to remove. 
### main.py
This file combines some functions from analyze_words and model to complete our program's user interface. The user will be prompted by the UI to input their review and this will call on analyze_word's "processing" to turn the data into tokens. Using the best combination as indicated by model.py, as well as the idf dictionary and list of stop words, this text input will be turned into an array that matches our model's predictors. Then, it will call on our saved model to predict the appropriate star rating based on that array, before printing it to the user.

## FOLDERS

### iPython_Tests
This contains jupyter notebook used for testing. In order to test that our program was accurate, we tested against various amounts of ratios between training and testing data and found that our model was consistently successful, even when given a smaller amount of traning data. 
### optimal_args
This folder contains all of the optimal arguments for our final model, created by model.py and used in the main.py. 
### scraped_data
This contains all of the raw, scraped data from Yelp.
### test_data
This contains the data that we test on, aka what our merged_data.py creates. 

## CONCLUSION

### On optimizing the model
We optimized our model using the standard training-testing split 80-20 as well as a 5-95 split. Our best combination (ngram, lemmatize, num_stop_words, alpha) was: (1, False, 0, 0.001) for the first split and (1, False, 0, 0.1) for the second. The resulting combination was mostly similar, with the exception of the alpha parameter. This indicates that our optimizing function is more or less robust. 

### Downsides
Our program largely depends on wording, not sentiment. Humans are able to detect inflection and tone when reading whereas our program cannot. Because of the time constraints of this project, we were unable to implement a program that can detect sarcasm and therefore, sometimes mixes up reviews that were meant to be read ironically, as literally. However, when given a robust review of honest opinions and feelings towards a restaurant, our program is able to accurately predict the star rating most of the time. 