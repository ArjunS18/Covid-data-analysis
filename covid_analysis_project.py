# -*- coding: utf-8 -*-
"""Covid analysis project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kh1eyJ8BogKlCDrGUkCuZ2-_5DkT9kSt

Covid Dataset from Github:

https://github.com/owid/covid-19-data/blob/master/public/data/owidcovid-data.csv

The dataset contains covid data for all countries from Jan 2020 to Jan 2022. The dataset provides
insights about the number of active cases in the country, number of deaths, number of vaccinated
people and much more.
A detailed description of all the variables present in the dataset can be found below:

https://github.com/owid/covid-19-data/tree/master/public/data

**Project summary:**

Cleaned the data, checked for outliers and normalized the data using log normal transformation

Classified the data into different categories based on the severity of new_cases

Trained Decision tree and KNN classfication algorithm and compared the accuracy between the models.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import *
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

#Function to find top countries list based on total cases 
#temp_df - filtered dataframe to find the top n countries
#colnames - group the dataframe based on this value
#sort_col - sort the dataframe based on this value
#count - default value is 0, can be changed based on requirements
#parameter out - top_n_df
def top_n_list(temp_df, colnames, sort_col = '', count = 0):
    group_df = temp_df.groupby(colnames).sum().reset_index()
    if sort_col:
        top_n_df = group_df.sort_values(by = sort_col, ascending = False)
        if count > 0:
            return top_n_df.head(count)
        else:
            return top_n_df
    else:
        return None

#Function to draw bar charts
#xaxis_val, yaxis_val - used for plotting values in respective axes
#xaxis_name, yaxis_name - label for respective axes
#tile_name - default - None, can be changed to give proper chart titles
def draw_bar_chart(xaxis_val, yaxis_val, xaxis_name, yaxis_name, title_name = None):
    ax = plt.subplot()
    plt.bar(xaxis_val,yaxis_val)
    plt.title(title_name)
    plt.xlabel(xaxis_name)
    #change orientation of xaxis-labels to avoid overlapping
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    plt.ylabel(yaxis_name)
    plt.show()

#Function to normalize the data.
#normalize_df - dataframe to be normalized
#colnames - column names of the dataframe to be normalized
#scaler - Scaler object based on which normalization will be done
#boxplot - Default - False, if set to True, Boxplot will be shown
#parameter out - normalize_df - normalized dataframe
def normalization(normalize_df, colnames, scaler, boxplot = False):
    scaler_df = normalize_df[colnames]
    normalize_df[colnames] = scaler.fit_transform(scaler_df.values)
    if boxplot:
        sns.boxplot(x="variable", y="value", data=pd.melt(normalize_df[colnames]))
    return normalize_df

# Function to split the data frame into test and train
def split_data(split_df, independent_vars, target_var, test_size_val = 0.3, random_state_val = 100):
  
    # Separating the target variable
    X = split_df[independent_vars]
    Y = split_df[target_var]
    
    # Splitting the dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split( 
    X, Y, test_size = test_size_val, random_state = random_state_val)
      
    return X, Y, X_train, X_test, y_train, y_test

# Function to perform training with entropy.
#parameter_in - Two training sets - X_train (independent), y_train(dependent)
def decisiontree_using_entropy(X_train, y_train):
  
    # Decision tree with entropy
    decision_entropy = DecisionTreeClassifier(
            criterion = "entropy", random_state = 100,
            max_depth = 5, min_samples_leaf = 5)
  
    # Performing training
    decision_entropy.fit(X_train, y_train)
    return decision_entropy

# Function to make predictions
def prediction(X_test, classifier_object):
  
    y_pred = classifier_object.predict(X_test)
    #print("Predicted values:")
    #print(y_pred)
    return y_pred

# Function to calculate accuracy of the model
def calculate_accuracy(y_test, y_pred, acc_return = False):
    
    if not acc_return:
        print("Confusion Matrix: ",
              confusion_matrix(y_test, y_pred))
      
        print ("Accuracy : ",
               accuracy_score(y_test,y_pred)*100)
    
        print("Report : ",
              classification_report(y_test, y_pred))
        
    acc = accuracy_score(y_test,y_pred)*100
    return acc



from google.colab import files
covid = files.upload()

from google.colab import files
countries = files.upload()

#read csv file
df = pd.read_csv('owid-covid-data.csv')
df_bkup = df.copy(deep=True)

#read countries csv file to clean location column
country_name = pd.read_csv('countries.csv')

#Check the list of column names in the dataset
colname_list = df.columns.values.tolist()
df.replace(np.NaN, 0, inplace=True)

#splice the dataset as per requirements 
filter_df = df.filter(['iso', 'continent', 'location', 'new_cases', 'new_deaths'])

#Original covid data set has unnecessary location names such as World, High income. Remove them.
country_filter_df = filter_df[filter_df['location'].isin(list(country_name['name']))]

#find top_n_countries based on total_cases
group_by_col = ['location']
sort_by_col = ['new_cases']

top_df = top_n_list(country_filter_df, group_by_col, sort_by_col)
top_df

#As new_cases value of countries such as Tonga, Nauru, Tuvalu are infinitesimal,
#we will consider only top 120 countries
top_df = top_n_list(country_filter_df, group_by_col, sort_by_col, 120)
top_df_loc = top_df.head(10)
#plot bar chart for top n countries. Limit to 10 to 20 counties to get clean graph
draw_bar_chart(top_df_loc['location'], top_df_loc['new_cases'], 'location', 'new_cases', 'Top_n_countries_total_covid_cases')

top_df = top_df.sort_values(by = 'location', ascending = True)
top_df

# Add category labels for new_cases.
category = pd.cut(top_df['new_cases'], bins = [-1,100000,1000000,1000000000], labels = ["L","M","H"])

# Add the binned values as a new categorical feature
top_df["severity"] = category
top_df.reset_index(drop=True)

#check for outliers
outlier_df = top_df.copy(deep=True)
check_outlier_df = top_df.filter(['new_cases', 'new_deaths'])
sns.boxplot(x="variable", y="value", data=pd.melt(check_outlier_df))

#As the new_cases grow exponentially, it is better to use lognormal transformation
outlier_df['log_new_cases'] = np.log(outlier_df['new_cases'])
outlier_df['log_new_deaths'] = np.log(outlier_df['new_deaths'])
outlier_df.reset_index(drop=True, inplace=True)
sns.distplot(outlier_df['log_new_deaths'])

#Decision tree
#use label encoder to convert column location from string to numeric data
le = LabelEncoder()
outlier_df['location_index']= le.fit_transform(outlier_df['location'])
independent_vars_col = ['location_index','log_new_cases', 'log_new_deaths']
outlier_df[['location_index', 'severity']].head(25)
target_var_col = ['severity']
X, Y, X_train, X_test, Y_train, Y_test = split_data(outlier_df, independent_vars_col, target_var_col)

decisiontree_entropy = decisiontree_using_entropy(X_train, Y_train)
decisiontree_entropy

y_pred_entropy = prediction(X_test, decisiontree_entropy)
calculate_accuracy(Y_test, y_pred_entropy)

#KNN
acc_rate = []
#Train the model with different values for n_neighbors
for n_neighbor in range(2,40):
    
    knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski', metric_params=None, n_jobs=1, n_neighbors=n_neighbor, p=2, weights='uniform')
    knn.fit(X_train,Y_train.values.ravel())
    pred_i = prediction(X_test, knn)
    acc_rate.append(calculate_accuracy(Y_test, pred_i, True))

plt.figure(figsize=(10,6))
plt.plot(range(2,40),acc_rate,color='blue', linestyle='dashed', marker='o',
         markerfacecolor='red', markersize=10)
plt.title('Accuracy vs. K Value')
plt.xlabel('K')
plt.ylabel('Model Accuracy')

#When n_neighbor value is 3, we achieve highest accuracy in the model i.e 72%. 
knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski', metric_params=None, n_jobs=1, n_neighbors=3, p=2, weights='uniform')
knn.fit(X_train,Y_train.values.ravel())
knn_pred = prediction(X_test, knn)
calculate_accuracy(Y_test, knn_pred)