from config import api_key
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

# Start .csv
with open('match_history.csv','w', newline='', encoding='utf-8-sig') as refFile:
	writer = csv.writer(refFile)
	hdr = ["gameId","start_time", "duration", "queue", "win", "championId","role","lane","kills","deaths","assists", "damage_dealt", "gold", "cs", \
		"cspm_0", "cspm_10", "cspm_20", "xppm_0", "xppm_10", "xppm_20", "gpm_0", "gpm_10", "gpm_20", "cspm_diff_0", "cspm_diff_10", "cspm_diff_20", \
		"xppm_diff_0", "xppm_diff_10", "xppm_diff_20"]
	writer.writerow(hdr)

	# Get the last 100 matches .. 
	for i in range(2):
		time.sleep(3)
		ind = i * 100
		matches_params = {"api_key":my_key, "beginIndex": ind}
		url = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id
		matches_resp = requests.get(url, matches_params)
		matches_resp_json = matches_resp.json()
		# queue IDs
		# aram = 450, solo/duo = 420, flex = 440, norm draft = 400, clash = 700
		matches = matches_resp_json["matches"]

		for j, match in enumerate(matches):
			time.sleep(3)
			url = "https://na1.api.riotgames.com/lol/match/v4/matches/" + str(match["gameId"])
			match_resp = requests.get(url, matches_params)
			match_info = match_resp.json()
			print(match["gameId"], j+ind)

			# Match info
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
				cspm_0 = player_info["timeline"]["creepsPerMinDeltas"]["0-10"]
				xppm_0 = player_info["timeline"]["xpPerMinDeltas"]["0-10"]
				gpm_0 = player_info["timeline"]["goldPerMinDeltas"]["0-10"]

				#print(player_info["timeline"])
				# These variables might not be available
				if "10-20" in player_info["timeline"]["creepsPerMinDeltas"]:
					cspm_10 = player_info["timeline"]["creepsPerMinDeltas"]["10-20"]
					xppm_10 = player_info["timeline"]["xpPerMinDeltas"]["10-20"]	
					gpm_10 = player_info["timeline"]["goldPerMinDeltas"]["10-20"]
				else:
					cspm_10 = 0
					xppm_10 = 0
					gpm_10 = 0
				if "20-30" in player_info["timeline"]["creepsPerMinDeltas"]:
					cspm_20 = player_info["timeline"]["creepsPerMinDeltas"]["20-30"]
					xppm_20 = player_info["timeline"]["xpPerMinDeltas"]["20-30"]
					gpm_20 = player_info["timeline"]["goldPerMinDeltas"]["20-30"]
				else:
					cspm_20 = 0
					xppm_20 = 0
					gpm_20 = 0
				# # Diffs exist
				if "csDiffPerMinDeltas" in player_info["timeline"]:
					cspm_diff_0 = player_info["timeline"]["csDiffPerMinDeltas"]["0-10"]
					if "10-20" in player_info["timeline"]["csDiffPerMinDeltas"]:
						cspm_diff_10 = player_info["timeline"]["csDiffPerMinDeltas"]["10-20"]
					else:
						cspm_diff_10 = 0
					if "20-30" in player_info["timeline"]["csDiffPerMinDeltas"]:
						cspm_diff_20 = player_info["timeline"]["csDiffPerMinDeltas"]["20-30"]
					else:
						cspm_diff_20 = 0
				else:
					cspm_diff_0 = 0
					cspm_diff_10 = 0
					cspm_diff_20 = 0
				
				if "xpDiffPerMinDeltas" in player_info["timeline"]:
					xppm_diff_0 = player_info["timeline"]["xpDiffPerMinDeltas"]["0-10"]
					if "10-20" in player_info["timeline"]["xpDiffPerMinDeltas"]:
						xppm_diff_10 = player_info["timeline"]["xpDiffPerMinDeltas"]["10-20"]
					else:
						xppm_diff_10 = 0
					if "20-30" in player_info["timeline"]["xpDiffPerMinDeltas"]:
						xppm_diff_20 = player_info["timeline"]["xpDiffPerMinDeltas"]["20-30"]
					else:
						xppm_diff_20 = 0
				else:
					xppm_diff_0 = 0
					xppm_diff_10 = 0
					xppm_diff_20 = 0


			row = [match["gameId"],start_time, duration, queue, win, championId, role, lane, kills, deaths, assists, damage_dealt, gold, cs, \
				cspm_0, cspm_10, cspm_20, xppm_0, xppm_10, xppm_20, gpm_0, gpm_10, gpm_20, \
				cspm_diff_0, cspm_diff_10, cspm_diff_20, xppm_diff_0, xppm_diff_10, xppm_diff_20]	
			writer.writerow(row)