from config import api_key
from gcp import add_match_table
import requests
import numpy as np
import csv
import time
import os
from google.cloud import bigquery

print("Updating...")
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
		#filename = 'match_history.csv'
		table_id = "league-of-legends-analysis." + dataset_name + "." + table_name # TODO clean up
		query = f""" SELECT MAX(gameId)
				FROM `{table_id}`"""
		# Set up the query
		query_job = client.query(query)
		data = query_job.to_dataframe()
		last_gameId = data.iat[0,0] # Get value (float)

		my_key = api_key
		# Get the account ID
		summoner_name = "dragonsp"
		account_params = {"summonerName":summoner_name,"api_key":my_key}
		url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name
		account_resp = requests.get(url, account_params)
		account_resp_json = account_resp.json()
		print(account_resp_json)
		account_id = account_resp_json["accountId"] # GkeXzed8ujNQajjS1ZpY_9T6zSbm82otcRk2CR9aIS06UCY 
		puuid = account_resp_json["puuid"] # for v5 of API
		ind = 0
		updated = False
		filename = 'new_games.csv'
		reget_count = 0
		# Keep searching through history until an existing match is found
		with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
			writer = csv.writer(f)
			hdr = ["gameId","start_time", "duration", "queue", "win", "championName","role","lane","pos","kills","deaths","assists", "damage_to_champs", "damage_to_obj", \
			"damage_taken", "gold", "cs", "vision_score", "longest_life"]
			writer.writerow(hdr)
			while not updated:
				#time.sleep(2)
				begin_ind = ind * 100
				matches_params = {"api_key":my_key, "start": ind, "count" : 100}
				url = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids"
				matches_resp = requests.get(url, matches_params)
				matches_resp_json = matches_resp.json()
				# queue IDs
				# aram = 450, solo/duo = 420, flex = 440
				matches = matches_resp_json

				for j, match in enumerate(matches):
					# Since the response is sorted from most recent to oldest, when an existing game is found, we can exit
					if match == last_gameId:
						print("Updated")
						updated = True
						break
					else:
						#time.sleep(2)
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
						
						# Ignore non-SUmmoner's RIft
						queue = match_info["queueId"]
						if queue == 400 or queue == 420 or queue == 430 or queue == 440 or queue == 700:
							# TODO: function for getting the data needed in a row - input "match_info", "summoner_name", output "row"
							start_time = match_info["gameCreation"]/1000
							duration = match_info["gameDuration"]
							players_info = match_info["participants"]
							for player in players_info:
								if summoner_name == player["summonerName"]:
									my_participant_id = player["participantId"]

							player_info = match_info["participants"][my_participant_id-1]
							#print(player_info)
							win = player_info["win"] 
							assists = player_info["assists"]
							championName = player_info["championName"]
							deaths = player_info["deaths"]
							damageToObj = player_info["damageDealtToObjectives"]
							gold = player_info["goldEarned"]
							pos = player_info["individualPosition"] # is this from champ select or ingame?
							kills = player_info["kills"]
							lane = player_info["lane"]
							longestLife = player_info["longestTimeSpentLiving"]
							role = player_info["role"]
							damageToChamps = player_info["totalDamageDealtToChampions"]
							damageTaken = player_info["totalDamageTaken"]
							cs = player_info["totalMinionsKilled"] + player_info["neutralMinionsKilled"] # TODO: look into this
							visionScore = player["visionScore"] #breakdown to wards placed/killed?

							row = [match, start_time, duration, queue, win, championName, role, lane, pos, kills, deaths, assists, damageToChamps, damageToObj, damageTaken, \
								gold, cs, visionScore, longestLife]
							writer.writerow(row)
				ind += 1
		# Load new games to BQ database
		add_match_table(filename)
	else:
		print("Table not found")
else:
	print("Dataset not found.")
