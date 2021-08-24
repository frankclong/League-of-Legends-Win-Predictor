from config import api_key
from gcp import create_match_table
import requests
import numpy as np
import csv
import time
from google.cloud import bigquery

client = bigquery.Client(project="league-of-legends-analysis")

my_key = api_key
print(my_key)

#GkeXzed8ujNQajjS1ZpY_9T6zSbm82otcRk2CR9aIS06UCY
# Get the account ID
summoner_name = "dragonsp"
account_params = {"summonerName":summoner_name,"api_key":my_key}
url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name
account_resp = requests.get(url, account_params)
account_resp_json = account_resp.json()
print(account_resp_json)
account_id = account_resp_json["accountId"] 
puuid = account_resp_json["puuid"] # TODO update to use puuid for v5 of API
# h3EPcgcb77eWFV5zuptjJD1He1Y1xoDsU5r4E_olj6Dpb_ev2LAvEbWXb0zBDtwC7nc_ypAMii7_jA

reget_count = 0
# Get the last 1000 matches .. 
for i in range(4, 10):
    time.sleep(2)
    ind = i * 100
    matches_params = {"api_key":my_key, "start": ind, "count" : 100}
    url = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids"
    matches_resp = requests.get(url, matches_params)
    matches_resp_json = matches_resp.json()
    # queue IDs
    # aram = 450, solo/duo = 420, flex = 440, norm draft = 400, clash = 700
    matches = matches_resp_json

    for j, match in enumerate(matches):
        time.sleep(2)
        url = "https://americas.api.riotgames.com/lol/match/v5/matches/" + str(match)
        match_resp = requests.get(url, matches_params)
        match_resp_json = match_resp.json() # sometimes get 504 errors
        print(match, j+ind)
    
        if match_resp.status_code == 404:
            print("Data not found")
            continue

        # Match info
        # Keep calling until success
        while "info" not in match_resp_json:
            match_resp = requests.get(url, matches_params)
            match_resp_json = match_resp.json()
            print("RE-Getting...")
            reget_count += 1
        match_info = match_resp_json["info"]
        queue = match_info["queueId"]
        players_info = match_info["participants"]
        # Ignore ARAM
        if queue != 450:
            for player in players_info:
                if summoner_name == player["summonerName"]:
                    my_participant_id = player["participantId"]

            player_info = match_info["participants"][my_participant_id-1]
            cs = player_info["totalMinionsKilled"] + player_info["neutralMinionsKilled"] 

            # Run query to update database
            query_text = f"""
                UPDATE `league-of-legends-analysis.matches.match-details-v2`
                SET cs = {cs}
                WHERE gameId = "{match}"
                """
            query_job = client.query(query_text)

            # Wait for query job to finish.            
            query_job.result()

            print(f"DML query modified {query_job.num_dml_affected_rows} rows.")