# THE YELP RATING PREDICTOR

Hello, and welcome to our final CMSC 12200 project: "The Yelp Rating Predictor"!

Our goal for this project was to create a program that predicts a Yelp rating (out of 5 stars) for a review using the Linear SVM model. First, we have a short introduction on how to use the program. Then, we will be going into what each file does and how it contributes to the overarching goal of the project. Lastly, we will evaluate the scope of what our project can do and the limitations that come with it. 

## RUNNING THE PROGRAM

Make sure you have all of the libraries downloaded. Run "python3 main.py" in the terminal or "run main.py" in jupyter notebook. Type in your review and press enter to get the star rating.

## FILES

### util.py
This file contains utility functions for dealing with URLs.

### crawl_and_scrape.py
This file was created to scrape the data necessary for training our model. Using Beautiful Soup, this takes the Yelp landing page (e.g. https://www.yelp.com/search?cflt=restaurants&find_loc=Chicago%2C%20IL) for a given city and scrapes the URL for every restaurant in the city landing page. Then for every restaurant, it scrapes reviews into a CSV file. We have elected to create a separate CSV file for each restaurant as the crawling process takes a long time, and it would easier to continue scraping from when the scraping process times out.

One feature of this file contains the element of "sleeping" and a user-defined counter (where a higher number corresponds to a longer run-time but fewer pages skipped). Yelp attempts to block attempts for web-scraping, making it hard for an algorithm to go through the web pages without being blocked. With this caveat in mind, we created a feature such that during scraping, for each page, it would randomly "sleep" to try to bypass the Yelp's detection system and/or tries again "counter" many times if it fails, before giving up and skipping the page. This ended up working as we were able to collect more reviews than before. However, this comes at the cost of a longer runtime due to the random "sleeps" and more retries. 

Another feature of this file is that we've included a maximum number of reviews per restaurant parameter for users to decide upon crawling and scraping. This enables users to get reviews from a variety of restaurants at a faster rate because once this maximum number is reached, the crawler will skip to the next restaurant. This also allows for more equal distribution of reviews for each restaurant/cuisine because, in Yelp, some restaurants have around 8000 reviews while others only have around 1000 - 2000 reviews. 

### merge_data.py
This file contains one function that combines all restaurant reviews scraped using the functions in crawl_and_scrape.py into one DataFrame. Then, it grouped each review by rating and attempts to sample equally from each rating group to create a dataset with 10,000 reviews.

If there are insufficient reviews from any particular rating group, then we will adjust accordingly and simply accept all reviews from the rating group. Additional reviews will be sampled from other rating groups instead. The final DataFrame will be written into a CSV.

### analyze_words.py
This file focuses on processing the CSV file that contains the 10,000 balanced reviews (output of merged_data.py) and returning a DataFrame with the corpus' tokens as the columns and the TF-IDF values for each review as the rows. It considers the n-gram length, whether or not to lemmatize words, and how many stop words should be removed. 

Taking the CSV file, we first get rid of all non-English reviews. Then, we processed each review (stripping punctuations or special characters, lemmatization, etc.) and created a list of tokens for each review. Then, we generated stop words by ranking the words by frequency (from the most to least frequent) and took the top-n words (as indicated by the num_stop_words parameter) as our stop_words. We didn't use the default stop words library that is available because we thought that the most frequent words in restaurant reviews could potentially be different from other texts more generally. Then, we removed these chosen stop words from each review's token list. 

The last function in the file, get_df_idf_stops(), takes in parameters n (n-gram size), num_stop_words (number of stop words), and creates an array 'X' containing all vectorized tokens from the raw review dataset. It also returns the corresponding 'y_values'(Rating corresponding to text review) and 'vectorizer' object used.

### model.py
This file trains tests and saves our model. To evaluate the accuracy of each model, we calculated a weighted accuracy that allows us to penalize predictions more when they are further away from the actual rating (i.e. predicting a 5-star review as a 1 star). In the function "optimize_model", we cycled through combinations of parameters, namely: n-grams, number of stop words, and different variances of alphas to get the best combination that maximizes the accuracy of our model. Then, we used the output of this function in our "main_modelling" function where we further optimized the model by performing feature selection. The feature selection was done mainly using the sklearn library's feature selection method. 

Although feature selection reduced our overall accuracy (since it reduces the number of predictors in our model), it reduces the potential for overfitting. Given that our data comes exclusively from the US, reducing overfitting is important to make our model more robust in predicting reviews from a random user (of unknown location).

Then, "main_modelling" (after optimizing and feature selection) will save the best model as a PKL file, which is the model that we will use to predict the user's review input. It also saves the optimal vectorizer and selector in PKL files.

### main.py
This file combines selector, vectorizer, and model PKL files from the 'optimal_args' directory to complete our program's user interface. The user will be prompted by the UI to input their review. Before further tokenizing, the user input will be autocorrected (since reviews on Yelp contain little to no spelling mistakes due to autocorrection features on smartphones).

Using the files from 'optimal_args', the text input will be turned into an array that matches our model's feature selected predictors. Then, it will call on our saved model to predict the appropriate star rating based on that array, before printing it to the user.

### optimizing_results.txt
This file contains the print statements resulted from optimizing the model using different training-testing splits. 

## Directories

### iPython_Tests
This contains Jupyter notebooks that we used for testing. To test that our program was accurate, we tested against various amounts of ratios between training and testing data and found that our model was consistently successful, even when given a smaller amount of training data. This folder mainly contains scrap work that we did and is not relevant to the workings of our program. 

### optimal_args
This folder contains all of the optimal arguments for our final model, created by model.py and used in the main.py. 

### scraped_data
This contains all of the raw, scraped data from Yelp. Datasets are grouped based upon geographical locations. In our modeling, we used data from main cities in the United States such as New York, Chicago, and Las Vegas.

### test_data
This contains the data that we test on, aka what our merged_data.py creates. 

## CONCLUSION

### On optimizing the model
We optimized our model using the standard training-testing split 80-20 as well as a 5-95 split. Our best combination (ngram, num_stop_words, alpha) was: (2, 0, 0.0001) for the first split and (2, 0, 0.0001) for the second. The resulting combination was exactly the same. This indicates that our optimizing function is robust.

The print statements for our optimization can be found in the optimizing_results.txt file. 

It is interesting to note that the optimal number of stop words appears to be 0 from our testing. This is likely due to the limited number of unique words used in the context of restaurant reviews. As such, each word carries greater weight and even frequently appearing words have an impact on the overall judgment of the model.

### Limitations
Humans can detect satire and irony when reading whereas our program cannot. Because of the time constraints of this project, we were unable to implement a program that can detect sarcasm and therefore, sometimes mixes up reviews that were meant to be read ironically, literally. However, when given a robust review of honest opinions and feelings towards a restaurant, our program can accurately predict the star rating most of the time. That is, as long as users input reviews sincerely, the model can perform adequately.

### Extensions
There are geographical and intertemporal differences in word choice/structure of food reviews across regions and user demographics. We could create customized models for users, for instance, requesting the restaurant location (city) and user age to normalize for differences.
This could be enabled by categorizing reviews based on the location of the restaurant and the time of reviews created. 

The terminal interface could also be enhanced by the presence of build-in word/sentence complete scripts that assists users in coming up with reviews. Like the autocomplete feature on mobile phones, the terminal will display a drop-down list of possible next words for users during the input process.

### Important Caveat

It turns out that due to restrictions imposed by Yelp.com, subsequent review pages(after page 1, for each restaurant) do not contain the relevant review information in its HTML source code. Due to time constraints, we will not be changing our scraping code drastically. As such, we will be only collecting 20 reviews from each restaurant. The shortfall in reviews is made up by scraping data from more cities. This is made possible by setting the "max_rev_per_resto" parameter to 20.

In our attempts at scraping reviews, we used a 'counter' of 30 and could generate 2000-3000 reviews per city. We suggest using a VPN to do this.
