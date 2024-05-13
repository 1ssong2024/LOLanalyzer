COUNTRY = "americas"
import requests
API_KEY = "RGAPI-9c987b9f-3e79-4ce1-b069-6c2f0a89d2e4"
import json

name_url = 'https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4957699488/timeline'
headers = {'X-Riot-Token': API_KEY}
name_rsp = requests.get(name_url, headers=headers).json()
file_path = "timelinedatatest.json"

# Open the file in write mode and write the JSON data to it
with open(file_path, 'w') as file:
    json.dump(name_rsp, file)