# League-of-Legends-Win-Predictor
## Instructions
1. Enter your summoner ID into main.py and run it to retrieve and initial list of your 200 last matches. This can be increased by changing the counter
2. If more matches have been played, run the update_match.py file to retrieve them and add the data to the .csv file
3. Run load.py to clean the data and prepare for analysis

## Variables retrieved from the Riot API
* Game ID
* Start time
* Duration
* Queue
  * 400 - 5v5 Summoner's Rift Draft Pick
  * 420 - Solo/Duo
  * 430 - 5v5 Blind Pick
  * 440 - Flex
  * 450 - ARAM
  * 700 - Clash
  * Other custom game modes...
* Match result
* Champion ID
  * http://ddragon.leagueoflegends.com/cdn/6.24.1/data/en_US/champion.json (out of date)
* Role/Lane
* Kills
* Deaths
* Assists
* Damage dealt to champions
* Damage dealt to objectives 
* Damage taken
* Gold
* CS
* Vision score
* Longest life
* Potentially to add:
  * Team data - first blood, first tower, first inhib, first baron, first dragon, number of dragons etc.

## Analysis and Insights
Filters:
* Date
* Queue
* ChampID
* Match result
* Match duration
* Role-Lane

## Predictive Model
