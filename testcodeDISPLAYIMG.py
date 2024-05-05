from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_summoner_data_by_puuid(puuid):
    # Replace 'YOUR_API_KEY' with your Riot Games API key
    api_key = 'RGAPI-02aab05a-8684-4f1b-bcbd-c7dcfb0f99e7'
    region = 'na1'  # Change the region if necessary
    country = "americas"
    
    # URL for the Riot Games API to get summoner information by PUUID
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}'
    
    # URL for the Riot Games API to get match list by PUUID
    match_list_url = f'https://{country}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={api_key}'
    
    # Add API key to the request headers
    headers = {
        'X-Riot-Token': api_key
    }
    
    # Make the HTTP GET request to the Riot Games API to get summoner data
    summoner_response = requests.get(summoner_url, headers=headers)
    
    # Check if the request was successful
    if summoner_response.status_code == 200:
        summoner_data = summoner_response.json()
        profile_icon_id = summoner_data['profileIconId']  # Add this line to retrieve profile icon ID
        summoner_name = summoner_data['name']
        print(profile_icon_id)
        print(summoner_name)
        
        # Make the HTTP GET request to the Riot Games API to get match list
        match_list_response = requests.get(match_list_url, headers=headers)
        print(match_list_response)
        
        # Check if the request was successful
        if match_list_response.status_code == 200:
            matches = match_list_response.json()
            #matches = match_list_data['matches']
            return summoner_name, profile_icon_id, matches  # Return profile_icon_id along with summoner_name and matches
    return None, None, None  # Return None for all variables if the request fails

@app.route('/', methods=['GET', 'POST'])
def index():
    summoner_name = None
    profile_icon_url = None
    matches = None
    if request.method == 'POST':
        puuid = request.form['puuid']
        if puuid:
            summoner_name, profile_icon_id, matches = get_summoner_data_by_puuid(puuid)  # Update function call to get profile_icon_id
            if summoner_name:
                profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/10.25.1/img/profileicon/{profile_icon_id}.png'
    
    return render_template('index.html', summoner_name=summoner_name, profile_icon_url=profile_icon_url, matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
