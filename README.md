# MSc_Project_Repo

Name of Dissertation: Predicting Bitcoin Price Using Machine Learning

This project uses the Tensorflow Library specifically Keras to develope and create LSTM models for trying to predict Bitcoins price. The project has used 2 methods to compare predictability of the models and to see which one is better. The project contains 4 folders:

METHOD 1

Single LSTM (Which contain the most general code for a single variable LSTM model, which extracts its predictions to be used for feature selection)
Feature Selection (This one compiles all results from single variable LSTMs and uses Random Forest to determine the most important features when predicting the price)
Logistic Regression Single LSTM (This combines the results from the previous two and uses logistic regression after the LSTM outputs to increase predictability of the model)

METHOD 2 
Multivariate LSTM (This is a seperate method using Multivariate LSTM models with logistic regression instead of using method 1)
