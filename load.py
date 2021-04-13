# Load the csv data
import pandas as pd 

data = pd.read_csv('./match_history.csv', index_col = "gameId")
data = data.sort_values(by=['start_time'], ascending = False)


# Some filters
soloduo_filter = data['queue'] == 420 
flex_filter = data['queue'] == 440

data=data[(soloduo_filter) | (flex_filter)]
print(data.head())

# Get target column after filters applied
target = data['win']
print(target.head())

# Create model and train it