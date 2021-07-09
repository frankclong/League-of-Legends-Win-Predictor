from config import api_key
from gcp import create_match_table
import requests
import numpy as np
import csv
import time

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
# Start .csv
filename = 'match_history_gcp.csv'
with open(filename,'w', newline='', encoding='utf-8-sig') as refFile:
	writer = csv.writer(refFile)
	hdr = ["gameId","start_time", "duration", "queue", "win", "championName","role","lane","pos","kills","deaths","assists", "damage_to_champs", "damage_to_obj", \
		"damage_taken", "gold", "cs", "vision_score", "longest_life"]
	writer.writerow(hdr)

	# Get the last 1000 matches .. 
	for i in range(10):
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
			start_time = match_info["gameCreation"]/1000
			duration = match_info["gameDuration"]
			queue = match_info["queueId"]
			players_info = match_info["participants"]
			# Ignore ARAM
			if queue != 450:
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
				cs = player_info["totalMinionsKilled"] + player_info["neutralMinionsKilled"] 
				visionScore = player["visionScore"] #breakdown to wards placed/killed?

				row = [match, start_time, duration, queue, win, championName, role, lane, pos, kills, deaths, assists, damageToChamps, damageToObj, damageTaken, \
					gold, cs, visionScore, longestLife]
				writer.writerow(row)

print("Match history retrieved! See match_history.csv")
print("Regets: ", reget_count)
create_match_table(filename)