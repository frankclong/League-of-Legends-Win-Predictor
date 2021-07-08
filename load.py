# Load the csv data
import pandas as pd
from google.cloud import bigquery 


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
        query = f""" SELECT *
                FROM `{table_id}`
                ORDER BY gameId DESC"""
        # Set up the query
        query_job = client.query(query)
        data = query_job.to_dataframe()
    else:
        print(f"Table `{table_name}` not found.")   
else:
    print(f"Dataset `{dataset_name}` not found.")   


#data = pd.read_csv('./match_history.csv', index_col = "gameId")
#data = data.sort_values(by=['start_time'], ascending = False)

# Some filters
soloduo_filter = data['queue'] == 420 
flex_filter = data['queue'] == 440

data=data[(soloduo_filter) | (flex_filter)]
print(data.head())

# Get target column after filters applied
target = data['win']
print(target.head())

# Transform data - categorical variables, normalizing to time
data["kda"] = (data["kills"]+data["assists"])/(data["deaths"]+0.01)
norm_to_time = ["damage_to_champs", "damage_to_obj", "damage_taken", "gold", "cs", "vision_score"]
for var in norm_to_time:
    data[var + "_pm"] = data[var]/(data["duration"]/60/1000)

data['start_time'] = pd.to_datetime(data['start_time'],unit='s') - pd.Timedelta('04:00:00')
data['hour'] = data['start_time'].dt.hour

print(data.head())

model_cols = ["position", "duration", "hour", "damage_to_champs_pm", "damage_to_obj_pm", "damage_taken", "gold_pm", "cs_pm", "vision_score_pm", "longest_life", "kda", "kills", "deaths", "assists"]
model_data = data[model_cols]
model_data = pd.get_dummies(model_data)
print(model_data.head())


# Deal with missing values


# Create model and train it