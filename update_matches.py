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
if "matches" in dataset_ids:
	tables = client.list_tables("league-of-legends-analysis.matches")
	table_ids = list(map(lambda x: x.table_id, tables))
	if 'match-details' in table_ids:
		#filename = 'match_history.csv'
		table_id = "league-of-legends-analysis.testdataset.match-details"
		table_id = "league-of-legends-analysis.testdataset.test-table-2"
		query = f""" SELECT MAX(gameId)
				FROM `{table_id}`"""
		# Set up the query
		query_job = client.query(query)
		data = query_job.to_dataframe()
		last_gameId = data.iat[0,0] # Get value (int)

		my_key = api_key
		# Get the account ID
		summoner_name = "dragonsp"
		account_params = {"summonerName":summoner_name,"api_key":my_key}
		url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name
		account_resp = requests.get(url, account_params)
		account_resp_json = account_resp.json()
		print(account_resp_json)
		account_id = account_resp_json["accountId"] # GkeXzed8ujNQajjS1ZpY_9T6zSbm82otcRk2CR9aIS06UCY

		ind = 0
		updated = False
		filename = 'new_games.csv'
		reget_count = 0
		# Keep searching through history until an existing match is found
		with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
			writer = csv.writer(f)
			hdr = ["gameId","start_time", "duration", "queue", "win", "championId","role","lane","kills","deaths","assists", "damage_dealt", "gold", "cs", \
				"cspm_0", "cspm_10", "cspm_20", "xppm_0", "xppm_10", "xppm_20", "gpm_0", "gpm_10", "gpm_20", "cspm_diff_0", "cspm_diff_10", "cspm_diff_20", \
				"xppm_diff_0", "xppm_diff_10", "xppm_diff_20"]
			writer.writerow(hdr)
			while not updated:
				time.sleep(3)
				begin_ind = ind * 100
				matches_params = {"api_key":my_key, "beginIndex": begin_ind}
				url = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id
				matches_resp = requests.get(url, matches_params)
				matches_resp_json = matches_resp.json()
				# queue IDs
				# aram = 450, solo/duo = 420, flex = 440
				matches = matches_resp_json["matches"]

				for j, match in enumerate(matches):
					# Since the response is sorted from most recent to oldest, when an existing game is found, we can exit
					if str(match["gameId"]) == str(last_gameId):
						print("Updated")
						updated = True
						break
					else:
						time.sleep(3)
						url = "https://na1.api.riotgames.com/lol/match/v4/matches/" + str(match["gameId"])
						match_resp = requests.get(url, matches_params)
						match_info = match_resp.json()
						print(match["gameId"], j+ begin_ind)

						# Match info
						# Keep calling until success
						while "gameCreation" not in match_info:
							match_resp = requests.get(url, matches_params)
							match_info = match_resp.json()
							print("RE-Getting...")
							reget_count += 1
						start_time = match_info["gameCreation"]/1000
						duration = match_info["gameDuration"]
						queue = match_info["queueId"]
						players_info = match_info["participantIdentities"]
						# Ignore ARAM
						if queue != 450:
							for player in players_info:
								if summoner_name == player["player"]["summonerName"]:
									my_participant_id = player["participantId"]
							player_info = match_info["participants"][my_participant_id-1]
							#print(player_info)
							win = player_info["stats"]["win"] 
							championId = player_info["championId"]
							role = player_info["timeline"]["role"]
							lane = player_info["timeline"]["lane"]
							kills = player_info["stats"]["kills"]
							deaths = player_info["stats"]["deaths"]
							assists = player_info["stats"]["assists"]
							damage_dealt = player_info["stats"]["totalDamageDealt"]
							gold = player_info["stats"]["goldEarned"]
							cs = player_info["stats"]["totalMinionsKilled"]
							
							#print(player_info["timeline"])
							# These variables might not be available
							if "creepsPerMinDeltas" in player_info["timeline"]:
								cspm_0 = player_info["timeline"]["creepsPerMinDeltas"]["0-10"]
								if "10-20" in player_info["timeline"]["creepsPerMinDeltas"]:
									cspm_10 = player_info["timeline"]["creepsPerMinDeltas"]["10-20"]
								else:
									cspm_10 = ''
								if "20-30" in player_info["timeline"]["creepsPerMinDeltas"]:
									cspm_20 = player_info["timeline"]["creepsPerMinDeltas"]["20-30"]
								else:
									cspm_20 = ''
							else:
								cspm_0 = ''
								cspm_10 = ''
								cspm_20 = ''

							if "xpPerMinDeltas" in player_info["timeline"]:
								xppm_0 = player_info["timeline"]["xpPerMinDeltas"]["0-10"]
								if "10-20" in player_info["timeline"]["xpPerMinDeltas"]:
									xppm_10 = player_info["timeline"]["xpPerMinDeltas"]["10-20"]
								else:
									xppm_10 = ''
								if "20-30" in player_info["timeline"]["xpPerMinDeltas"]:
									xppm_20 = player_info["timeline"]["xpPerMinDeltas"]["20-30"]
								else:
									xppm_20 = ''
							else:
								xppm_0 = ''
								xppm_10 = ''
								xppm_20 = ''

							if "goldPerMinDeltas" in player_info["timeline"]:
								gpm_0 = player_info["timeline"]["goldPerMinDeltas"]["0-10"]
								if "10-20" in player_info["timeline"]["goldPerMinDeltas"]:
									gpm_10 = player_info["timeline"]["goldPerMinDeltas"]["10-20"]
								else:
									gpm_10 = ''
								if "20-30" in player_info["timeline"]["goldPerMinDeltas"]:
									gpm_20 = player_info["timeline"]["goldPerMinDeltas"]["20-30"]
								else:
									gpm_20 = ''
							else:
								gpm_0 = ''
								gpm_10 = ''
								gpm_20 = ''

							# # Diffs exist
							if "csDiffPerMinDeltas" in player_info["timeline"]:
								cspm_diff_0 = player_info["timeline"]["csDiffPerMinDeltas"]["0-10"]
								if "10-20" in player_info["timeline"]["csDiffPerMinDeltas"]:
									cspm_diff_10 = player_info["timeline"]["csDiffPerMinDeltas"]["10-20"]
								else:
									cspm_diff_10 = ''
								if "20-30" in player_info["timeline"]["csDiffPerMinDeltas"]:
									cspm_diff_20 = player_info["timeline"]["csDiffPerMinDeltas"]["20-30"]
								else:
									cspm_diff_20 = ''
							else:
								cspm_diff_0 = ''
								cspm_diff_10 = ''
								cspm_diff_20 = ''
							
							if "xpDiffPerMinDeltas" in player_info["timeline"]:
								xppm_diff_0 = player_info["timeline"]["xpDiffPerMinDeltas"]["0-10"]
								if "10-20" in player_info["timeline"]["xpDiffPerMinDeltas"]:
									xppm_diff_10 = player_info["timeline"]["xpDiffPerMinDeltas"]["10-20"]
								else:
									xppm_diff_10 = ''
								if "20-30" in player_info["timeline"]["xpDiffPerMinDeltas"]:
									xppm_diff_20 = player_info["timeline"]["xpDiffPerMinDeltas"]["20-30"]
								else:
									xppm_diff_20 = ''
							else:
								xppm_diff_0 = ''
								xppm_diff_10 = ''
								xppm_diff_20 = ''

						
							row = [match["gameId"],start_time, duration, queue, win, championId, role, lane, kills, deaths, assists, damage_dealt, gold, cs, \
								cspm_0, cspm_10, cspm_20, xppm_0, xppm_10, xppm_20, gpm_0, gpm_10, gpm_20, \
								cspm_diff_0, cspm_diff_10, cspm_diff_20, xppm_diff_0, xppm_diff_10, xppm_diff_20]	
							writer.writerow(row)

				ind += 1
	else:
		print("Table not found")
else:
	print("Dataset not found.")
