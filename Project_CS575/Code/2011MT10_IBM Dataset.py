# -*- coding: utf-8 -*-
"""IBM Dataset_CS575_MiniProject_2011MT10_.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FVCVKvmUJDSFpW2dnXdMZbh7h1Ara95k

### Submission by Durgesh Vikram Yadav (2011MT10)

# IBM Dataset
"""

#Importing Libraries
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
from datetime import datetime
import matplotlib.pyplot as plt 
import warnings
warnings.simplefilter('ignore')

#Downloading data
ibm = pdr.DataReader('IBM', 'yahoo', start=datetime(2014, 8, 1), end=datetime(2016, 11, 30))

#Exporting and saving as csv files
ibm.to_csv('IBM_stock.csv', sep=',')

#Printing the first few lines of data
ibm.head()

#Visulaizing the data
plt.figure(figsize=(12,5))
plt.plot(ibm['Close'], label='Close Price history')
plt.legend()
plt.title('Close Price history vs Time')

"""###ADF and KPSS Tests"""

#Importing libraries
from statsmodels.tsa.stattools import adfuller,kpss

"""a) ADF Test"""

def adf_test(atr):
    #Perform Dickey-Fuller test:
    timeseries = ibm[atr].dropna()
    print ('Results of Dickey-Fuller Test for ',atr,'\n')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
       dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)

#apply adf test on the series
adf_test('Close')

"""Since p value is greater than 0.05, therefore, we fail to reject the null hypothesis and the data has a unit root and is non-stationary.

b) KPSS Test
"""

def kpss_test(atr):
    timeseries = ibm[atr].dropna()
    print ('Results of KPSS Test for ',atr)
    kpsstest = kpss(timeseries, regression='c')
    kpss_output = pd.Series(kpsstest[0:3], index=['Test Statistic','p-value','Lags Used'])
    for key,value in kpsstest[3].items():
        kpss_output['Critical Value (%s)'%key] = value
    print (kpss_output)
kpss_test('Close')

"""From KPSS Test, the test statistic is greater than the critical value, we reject the null hypothesis (series is not stationary).

Both tests conclude that the series is not stationary -> series is not stationary

###ACF and PACF Tests

a) ACF Test
"""

from statsmodels.graphics.tsaplots import plot_acf
plot_acf(ibm['Close'].dropna(), lags=10)
plt.show()

"""b) PACF Test"""

from statsmodels.graphics.tsaplots import plot_pacf
plot_pacf(ibm['Close'])
plt.show()

"""From ACF and PACF plots, since more than 5% of the plot is outside the shaded region, the data is non stationary.

### Differencing to make data as stationary
"""

#Differencing the data
ibm['diff'] = ibm['Close'].diff(periods=1)

#Visulaizing the differenced data
ibm["diff"].plot()

# ADF Test of differenced data
adf_test('diff')

"""Since p value is less than 0.05, therefore, we reject the null hypothesis and the differenced data is stationary."""

# KPSS Test of differenced data
kpss_test('diff')

"""From KPSS Test, the test statistic is less than the critical value, we fail to reject the null hypothesis (differenced series is stationary).

Both tests conclude that the differenced series is stationary -> series is stationary.
"""

# ACF Test of differenced data
plot_acf(ibm['diff'].dropna(), lags=10)
plt.show()

# PACF Test of differenced data
plot_pacf(ibm['diff'].dropna(), lags=10)
plt.show()

"""From ACF and PACF plots, since less than 5% of the plot is outside the shaded region, the differenced data is stationary.

# ARIMA Model
"""

# Installing pmdarima package
!pip3 install pmdarima

# Importing ARIMA libraries
from statsmodels.tsa.arima_model import ARIMA
from pmdarima.arima import auto_arima

stepwise_model = auto_arima(ibm["Close"], start_p=1, start_q=1,
                           max_p=3, max_q=3, m=1,
                           start_P=0, seasonal=False,
                           d=1, D=0, trace=True,
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True)
print(stepwise_model.aic())

data = ibm['Close'].dropna().to_numpy()
n = int(len(data)*0.7)
train, test = data[:n], data[n:]

# Fitting Model
model = ARIMA(data, order=(1, 0, 1))
model_fit = model.fit()

# Make Prediction
from sklearn.metrics import mean_squared_error
from math import sqrt

yhat = model_fit.predict(0,len(data)-1)
rmse = sqrt(mean_squared_error(data, yhat))
print('RMSE Value is: ',rmse)

# Visualize Results
plt.figure(figsize=(12,5))
plt.plot(data,label='Data')
plt.plot(yhat,label='Predicted Data')
plt.title('ARIMA')
plt.legend()
plt.show()

"""---



---



---

# LSTM Model
"""

# Imporint Libraries
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

df1=ibm['Close']
date = (ibm.index)
scaler=MinMaxScaler(feature_range=(0,1))
df1=scaler.fit_transform(np.array(df1).reshape(-1,1))

# Splitting data
training_size = int(0.8*len(df1))
test_size = len(df1)-training_size
train_data = df1[0:training_size]
test_data = df1[training_size:len(df1)]

# Converting to dataset matrix
def create_dataset(data, steps=1):
	dataX, dataY = [], []
	for i in range(len(data)-steps-1):
		a = data[i:(i+steps), 0]   
		dataX.append(a)
		dataY.append(data[i + steps, 0]) 
	return np.array(dataX), np.array(dataY)

# Reshaping
steps = 5
X_train, y_train = create_dataset(train_data, steps)
X_test, ytest = create_dataset(test_data, steps)
X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)

# Fitting Model
model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(100,1)))
model.add(LSTM(50,return_sequences=True))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')
model.summary()
model.fit(X_train,y_train,validation_data=(X_test,ytest),epochs=100,batch_size=64,verbose=0)

# Prediction
train_predict=model.predict(X_train)
test_predict=model.predict(X_test)

# Inverse Transform
train_predict=scaler.inverse_transform(train_predict)
test_predict=scaler.inverse_transform(test_predict)
Y_train = scaler.inverse_transform(y_train.reshape(-1, 1))
Y_test = scaler.inverse_transform(ytest.reshape(-1, 1))

# Train data RMSE
rmse1 = np.sqrt(np.mean(np.power((np.array(Y_train)-np.array(train_predict)),2)))
print('RMSE Value of train data with LSTM model',rmse1)

# Test Data RMSE
rmse2 = np.sqrt(np.mean(np.power((np.array(Y_test)-np.array(test_predict)),2)))
print('RMSE Value of test data with LSTM model',rmse2)

# Visulaize Predictions
pre=5
plt.figure(figsize=(12,5))
plt.plot(date,scaler.inverse_transform(df1), label='Data')
plt.plot(date[pre+1:training_size],train_predict, label='Train Data Prediction', color='red')
plt.plot(date[training_size+pre+1:],test_predict, label='Test Data Prediction')
plt.legend()
plt.title('LSTM')
plt.show()

"""---



---



---

# Exponential Smoothing
"""

# Importing Libraries
from statsmodels.tsa.holtwinters import ExponentialSmoothing

data = ibm['Close'].to_numpy()
date = (ibm.index)

#Exponentital Smoothening
Exp_model = ExponentialSmoothing(ibm.Close,trend='mul',seasonal='mul',seasonal_periods=4)
ibm['Exp_Smoothening'] = Exp_model.fit(smoothing_level = 0.9,smoothing_slope= 0.1,smoothing_seasonal = 0.2).fittedvalues.shift(0)

#RMSE Value
rmse3 = np.sqrt(np.mean(np.power((np.array(data)-np.array(ibm.Exp_Smoothening)),2)))
print('RMSE value with Exponential Smoothing: ',rmse3)

#Visulaize Data and Prediction
plt.figure(figsize=(12,5))
plt.plot(date,data, label='Data')
plt.plot(date,ibm.Exp_Smoothening, label='Predicted Data',color = 'red')
plt.legend()
plt.title('Exponential Smoothing')

"""---



---



---

#Prohet Model
"""

#Importing Library
from fbprophet import Prophet

#Adding Date Column to DataFrame
ibm['Date'] = pd.date_range(start='8/1/2014', periods=len(ibm.Close), freq='D')
ibm_features = ibm[['Date','Close']]
ibm_features = ibm_features.rename(columns = {"Date":"ds","Close":"y"})

#Applying Prophet model
ibm_model = Prophet(daily_seasonality = True) # stock prices have daily seasonality
ibm_model.fit(ibm_features)

#Predicting for future 30 days
future = ibm_model.make_future_dataframe(periods = 30)
prediction = ibm_model.predict(future)

#Visualizing the results
plt.figure(figsize=(12,5))
plt.plot(prediction['ds'],prediction['yhat'],color='red',label='Most Likely')
plt.plot(prediction['ds'],prediction['yhat_lower'],label='Pessimistic')
plt.plot(prediction['ds'],prediction['yhat_upper'],label='Optimistic')
plt.plot(ibm_features['ds'],ibm_features['y'],label='Actual Data')
plt.legend()
plt.title('Prophet Model')
plt.show()