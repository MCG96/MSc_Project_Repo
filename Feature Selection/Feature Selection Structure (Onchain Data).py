# -*- coding: utf-8 -*-
"""Onchain.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ggh_bM-XhpncmdYRT1Y1NRUEYeP0SAfr

Actions:


1.   Create Single LSTM's for each variable you want to use and extract the testing size (10% aka 280 days from the predicted data into a new file which is the outputs)
2.   Use the single LSTM's together in a document which is then used for our feature selection. The "training_data" will be the lstsm's created including the lstm for historical price, and the "training_output" data will just be the actual historical price for the testing period that we extract.
3.   Once we have done the feature selection we will do our combined model variable models over again with only the features that are selected from the feature selection method this should increase the accuracy. 
4.   Do the same thing for all our multi variable models and we will finally have the finished results.
"""

pip install quandl

import quandl
from pandas import read_csv
import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from matplotlib import pyplot as plt

testing_set_size = 280

# Getting the predicted datasets
BTC_Difficulty = pd.read_csv('/content/BTC Difficulty Predictions.csv')
BTC_Block_Size = pd.read_csv('/content/Block Size Predictions.csv')
BTC_Cost_Per_Transaction = pd.read_csv('/content/Cost Per Transaction Predictions.csv')
BTC_Hash_Rate = pd.read_csv('/content/Hash Rate Predictions.csv')
BTC_Transaction_Confirmation_Time = pd.read_csv('/content/Transaction Confirmation Time Predictions.csv')
BTC_Wallet_Users = pd.read_csv('/content/Wallet Users Predictions.csv')
BTC_Exchange_Volume = pd.read_csv('/content/Exchange Volume Predictions.csv')

# Getting the historical data so we can do the last 280 days
# Setting our API key
quandl.ApiConfig.api_key = 'PLbHumzEHFzBSiCbDCMo'

# Getting the test data 
BTC_test_data = quandl.get('BCHAIN/MKPRU', start_date = "2020-03-28", end_date = "2021-01-01")
# Remove the 'Date' index
BTC_test_data = BTC_test_data.reset_index(drop = True)
BTC_test_data

merged_data = pd.concat([BTC_Difficulty, BTC_Block_Size, BTC_Cost_Per_Transaction, BTC_Hash_Rate, BTC_Transaction_Confirmation_Time, BTC_Wallet_Users, BTC_Exchange_Volume], axis="columns")
merged_data

# Merge the Prediction data with the Real Price data
merged_data_2 = pd.concat([merged_data,BTC_test_data], axis="columns")
merged_data_2.rename(columns={'Value':'Real Price'}, inplace=True)
merged_data_2

# Getting the training data columns
training_data_cols = merged_data_2.columns.values
training_data_cols = np.array(training_data_cols[0:len(training_data_cols) - 1].tolist())
training_data_cols

# Getting the training data
training_data = merged_data_2.values
training_data = training_data[:, :-1]
training_data

# Getting the training output which is the real price data 
training_output = np.array(merged_data_2['Real Price'])
training_output

"""**Creating Model**"""

model = ExtraTreesRegressor(n_estimators=100)
model.fit(training_data, training_output)

# display the relative importance of each attribute
weights = np.array(model.feature_importances_)
training_data_cols_matrix = np.expand_dims(training_data_cols, axis=1)
weights = np.expand_dims(weights, axis=1)

# Table output
table = np.concatenate([training_data_cols_matrix, weights], axis=1)
table = pd.DataFrame(table)
table.columns = ['Attribute', 'Weights']
table.to_csv('weights_importance.csv', index=False)
print(table)

# Plot output
plt.rcParams.update({'figure.autolayout': True})
plt.rcParams.update({'figure.figsize': (12.0, 8.0)})
plt.rcParams.update({'font.size': 14})
sorted_idx = model.feature_importances_.argsort()
plt.barh(training_data_cols[sorted_idx], model.feature_importances_[sorted_idx], color='green')
plt.xlabel("Random Forest Feature Importance")
plt.savefig('RFFI.png', dpi=1080, format='png')
plt.show()
plt.savefig('Feature Selection Onchain.png')