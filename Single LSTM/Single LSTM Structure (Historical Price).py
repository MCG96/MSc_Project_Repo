# -*- coding: utf-8 -*-
"""Historical Price.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1joHb11unGL7_8HBl52ekBgOn6PBERE27
"""

pip install Quandl

import quandl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from math import sqrt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from keras.models import Sequential
from keras.layers import LSTM
from keras import layers
from keras.layers import Dropout
from keras.layers import Dense
from keras.engine.training import optimizers

# This is related to amount of DAYS in my case change this into 280 days which is about 10% of our dataset) This means test data is from 27.03.2020
testing_set_size = 280

# Setting our API key
quandl.ApiConfig.api_key = 'PLbHumzEHFzBSiCbDCMo'

# Retrieving the data
BTC = quandl.get('BCHAIN/MKPRU', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_difficulty = quandl.get('BCHAIN/DIFF', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_wallet_users = quandl.get('BCHAIN/MWNUS', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_average_block_size = quandl.get('BCHAIN/AVBLS', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_hash_rate = quandl.get('BCHAIN/HRATE', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_cost_per_transaction = quandl.get('BCHAIN/CPTRA', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_transaction_confirmation_time = quandl.get('BCHAIN/ATRCT', start_date = "2013-04-29", end_date = "2021-01-01")
BTC_exchange_volume = quandl.get('BCHAIN/TRVOU', start_date = "2013-04-29", end_date = "2021-01-01")

# Merge the retrieved data
merged_data = pd.concat([BTC, BTC_difficulty, BTC_wallet_users, BTC_average_block_size, BTC_hash_rate, BTC_cost_per_transaction, BTC_transaction_confirmation_time, BTC_exchange_volume], axis="columns")
merged_data.columns = ['Historical Price', 'Difficulty', 'Wallet Users', 'Average Block Size', 'Hash Rate', 'Cost Per Transaction', 'Transaction Confirmation Time', 'Exchange Volume']
merged_data

"""**DEALING WITH MISSING VALUES**"""

# Checking for how many missing values
merged_data.isna().sum()

# Need to do something with missing values, we can assume the previous value due to the nature of our data so fill in with the previous value 
merged_data = merged_data.fillna(method='ffill')

merged_data.isna().sum()

"""**FROM HERE PICK OUT THE VARIABLE YOUR DOIN THE ANALYSIS WITH**"""

# Column we want 
BTC = merged_data['Historical Price']

# The data column taken need to be converted into a pandas dataframe since its a series and wont work with the rest of the code if we dont do this
BTC = pd.DataFrame(BTC)
type(BTC)

plt.figure(figsize=(15, 8))
plt.title('BTC Price History')
plt.plot(BTC) # Put in variable you want to plot and change the titles accordingly
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.savefig('Historical Graph_1.png')

# Makign it into an array
training_set = BTC.values

# Scaling
sc = MinMaxScaler(feature_range=(0, 1))
training_set_scaled = sc.fit_transform(BTC)

"""**Training and Test Sets**"""

# Making function to splitt the data into a training and test set 
X_train = []
y_train = []
for i in range(0, (len(training_set) - testing_set_size)):
    X_train.append(training_set_scaled[i:i+1, 0])
    y_train.append(training_set_scaled[i, 0])

# Making the training sets into numpy arrays
X_train, y_train = np.array(X_train), np.array(y_train)

# Reshape the training set to work in the LSTM model 
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# We should see 2525 days here if we got the function correct 
print(X_train.shape) 
print(y_train.shape)

"""**Setting up the model**"""

model = Sequential()
model.add(LSTM(units = 50,input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.3)) #The dropout rate is set to 30%, meaning one in 3.33 inputs will be randomly excluded from each update cycle.
model.add(Dense(1))

model.compile(loss='mse',optimizer='adam', metrics=['mean_squared_error'])
print(model.summary())

"""**Applying the model**"""

lstm_pred = model.fit(X_train,y_train,batch_size=30,epochs=40)

"""**We need the full data as inputs**"""

# We take the historical data which we started out with and extract the values
dataset_test = BTC

# The real data that will be used in plot later to check for prediction period 
real_BTC_price = dataset_test.iloc[(len(dataset_test) - testing_set_size):, 0:1].values

# We then scale all those values 
inputs = sc.transform(dataset_test)

"""**Testing set and predictions**"""

# Creating empty list for the test set 
X_test = []
for i in range((len(training_set) - testing_set_size), len(training_set)):
    X_test.append(inputs[i:i+1, 0])

# Creating the numpy array
X_test = np.array(X_test)
# Reshape the array to fit LSTM 
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Fit the model to test set so you make predictions
predicted_BTC_price = model.predict(X_test) 
# Reshape the answers back to a normal numpy array
predicted_BTC_price = np.reshape(predicted_BTC_price, (testing_set_size, 1))
# We need to unscale the results of the predictions to normal numbers 
predicted_BTC_price = sc.inverse_transform(predicted_BTC_price)

# Showing the predictions of the model for the 280 days 
print(predicted_BTC_price)

"""**Graph of the Model**"""

plt.figure(figsize=(15, 8))
plt.plot(real_BTC_price, color='black', label='Real')
plt.plot(predicted_BTC_price, color='green', label='Predicted BTC')
plt.title('Real vs Predicted BTC')
plt.xlabel('Days in Testing Period')
plt.ylabel('BTC Price $')
plt.legend()
plt.show()
plt.savefig('First Run Results_1.png')

"""**Evaluation**"""

# Now we want to meassure accuracy against y-test which is already normal numbers
mse = mean_squared_error(real_BTC_price, predicted_BTC_price)

rmse = sqrt(mean_squared_error(real_BTC_price, predicted_BTC_price))

mape = np.round((mean_absolute_percentage_error(real_BTC_price, predicted_BTC_price) * 100), 4)

mae = mean_absolute_error(real_BTC_price, predicted_BTC_price)

print("Mean Square Error (MSE):", mse)
print("Root Mean Square Error (RMSE):", rmse)
print("Mean Absolute Error (MSE):", mae)
print(f'Mean Absolute Percentage Error (MAPE): {mape} %')

"""**Grid Search**"""

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV

# Create a function that will return a model with optimized parameters
def build_classifier(optimizer):
     grid_model = Sequential()
     grid_model.add(LSTM(units = 50,input_shape=(X_train.shape[1], 1)))
     grid_model.add(Dropout(0.3))
     grid_model.add(Dense(1))
     # Notice that below the optimizer is not adam but the function itself
     grid_model.compile(loss = 'mse',optimizer = optimizer, metrics = ['mean_squared_error'])
     return model

# Create a new model with the grid function built in 
grid_model = KerasClassifier(build_fn = build_classifier)

# Check which parameters you want the model to run through
parameters = {'batch_size' : [1,5,10,20,30,40,50],'epochs' : [5,10,20,30,40,50,60],'optimizer' : ['adam','Adadelta']}

# Now create the gridsearch, (n_jobs is either 1 for how many jobs to run in paraless, -1 means using all processors. cv is cross validation specified to 3 folds) 
grid_search  = GridSearchCV(estimator = grid_model, param_grid = parameters, n_jobs =-1, cv = 3)

# Run the gridsearch
grid_search = grid_search.fit(X_train,y_train)

# Tell me what the best parameters are
print("Best: %f using %s" % (grid_search.best_score_, grid_search.best_params_))

"""**Now use the new parameters in the model and get the new predictions that we will want to extract to our outcome file.**"""

new_model = Sequential()
new_model.add(LSTM(units = 50,input_shape=(X_train.shape[1], 1)))
new_model.add(Dropout(0.3)) #The dropout rate is set to 30%, meaning one in 3.33 inputs will be randomly excluded from each update cycle.
new_model.add(Dense(1))

new_model.compile(loss='mse',optimizer='adam', metrics=['mean_squared_error'])

# CHANGE batch size and epochs according to resutls before running 
lstm_pred = new_model.fit(X_train,y_train,batch_size=1,epochs=5)

# Fit the model to test set so you make predictions
predicted_BTC_price = new_model.predict(X_test) 
# Reshape the answers back to a normal numpy array
predicted_BTC_price = np.reshape(predicted_BTC_price, (testing_set_size, 1))
# We need to unscale the results of the predictions to normal numbers 
predicted_BTC_price = sc.inverse_transform(predicted_BTC_price)

# Showing the predictions of the model for the 280 days 
print(predicted_BTC_price)

plt.figure(figsize=(15, 8))
plt.plot(real_BTC_price, color='black', label='Real')
plt.plot(predicted_BTC_price, color='orange', label='Predicted BTC')
plt.title('Real vs Predicted BTC')
plt.xlabel('Days in Testing Period')
plt.ylabel('BTC Price $')
plt.legend()
plt.show()
plt.savefig('Second Run Results_1.png')

# Now we want to meassure accuracy against y-test which is already normal numbers
mse = mean_squared_error(real_BTC_price, predicted_BTC_price)

rmse = sqrt(mean_squared_error(real_BTC_price, predicted_BTC_price))

mape = np.round((mean_absolute_percentage_error(real_BTC_price, predicted_BTC_price) * 100), 4)

mae = mean_absolute_error(real_BTC_price, predicted_BTC_price)

print("Mean Square Error (MSE):", mse)
print("Root Mean Square Error (RMSE):", rmse)
print("Mean Absolute Error (MSE):", mae)
print(f'Mean Absolute Percentage Error (MAPE): {mape} %')

"""**Save the new improved model predictions to a new file**"""

# Create into a pandas dataframe 
predictions = pd.DataFrame(predicted_BTC_price)

predictions.columns = ['Predicted Price']

# Save the predictions to a new file
predictions.to_csv('BTC Price Predictions.csv', index = False)