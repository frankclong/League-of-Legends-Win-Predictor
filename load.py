# Load the csv data
import pandas as pd
import numpy as np
from google.cloud import bigquery 

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier	
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# Query database to get the greatest gameId
project_id = 'league-of-legends-analysis'
client = bigquery.Client(project=project_id)
datasets = list(client.list_datasets()) 
dataset_ids = list(map(lambda x: x.dataset_id, datasets))
dataset_name = "matches"
if dataset_name in dataset_ids:
    tables = client.list_tables("league-of-legends-analysis." + dataset_name)
    table_ids = list(map(lambda x: x.table_id, tables))
    table_name = "match-details-v2"

    if table_name in table_ids:
        table_id = "league-of-legends-analysis." + dataset_name + "." + table_name # TODO clean up
        query = f""" SELECT DISTINCT *
                FROM `{table_id}`
                ORDER BY start_time"""
        # Set up the query
        query_job = client.query(query)
        data = query_job.to_dataframe()
    else:
        print(f"Table `{table_name}` not found.")   
else:
    print(f"Dataset `{dataset_name}` not found.")   

# Some filters
soloduo_filter = data['queue'] == 420 
flex_filter = data['queue'] == 440

# ranked only
data=data[(soloduo_filter) | (flex_filter)]
print(data.head())

# Transform data - categorical variables, normalizing to time
data["kda"] = (data["kills"]+data["assists"])/(data["deaths"]+0.01)
norm_to_time = ["damage_to_champs", "damage_to_obj", "damage_taken", "gold", "cs", "vision_score"]
for var in norm_to_time:
    data[var + "_pm"] = data[var]/(data["duration"]/60/1000)

data['start_time'] = pd.to_datetime(data['start_time'],unit='s') - pd.Timedelta('04:00:00')
data['hour'] = data['start_time'].dt.hour

# New features
# First game
# Fatigue 

print(data.head())

model_cols = ["position", "duration", "hour", "damage_to_champs_pm", "damage_to_obj_pm", "damage_taken", "gold_pm", "cs_pm", "vision_score_pm", "longest_life", "kda", "kills", "deaths", "assists"]
model_data = data[model_cols]
# Filter by position here?
model_data = pd.get_dummies(model_data)
print(model_data.head())

# Get target column after filters applied
target = data['win']*1.0
print(target.head())

# Deal with missing values

# Visualizations
def spread(variable_of_interest, data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.catplot(x="position", y=variable_of_interest, hue="win", kind="swarm", data=data)
    plt.show()

#spread("cs_pm", data)

# Create model and train it
model = RandomForestClassifier(n_estimators=100, random_state=0)
game_data_train, game_data_valid, result_train, result_valid = train_test_split(model_data, target,train_size=0.8,random_state = 0)
model.fit(game_data_train, result_train)

def validate(game_data, result):
    # Validate model
    ## Single validation
    game_data_train, game_data_valid, result_train, result_valid = train_test_split(game_data, result,train_size=0.8,random_state = 0)
    model.fit(game_data_train, result_train)
    preds = model.predict(game_data_valid)
    print(list(preds))
    print(list(result_valid))
    error = mean_absolute_error(preds, result_valid)
    print("Single-Validation:", error)

    ## Cross-validation
    scores = -1 * cross_val_score(model, game_data, result, cv = 5, scoring = 'neg_mean_absolute_error')
    print("Cross-validation:", scores.mean())

def analyze(game_data, result):
    # SHAP analysis
    import shap
    model = RandomForestClassifier(n_estimators=100, random_state=0)
    game_data_train, game_data_valid, result_train, result_valid = train_test_split(game_data, result,train_size=0.8,random_state = 0)
    model.fit(game_data_train, result_train)
    # Create object that can calculate shap values
    explainer = shap.TreeExplainer(model)

    # calculate shap values. This is what we will plot.
    # Calculate shap_values for all of val_X rather than a single row, to have more data for plot.
    shap_values = explainer.shap_values(game_data_valid)

    # Make plot. Index of [1] is explained in text below.
    shap.summary_plot(shap_values[1], game_data_valid)

validate(model_data, target)
analyze(model_data, target)
