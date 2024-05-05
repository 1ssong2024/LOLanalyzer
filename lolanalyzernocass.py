import requests
from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# Your API Key
API_KEY = "RGAPI-b8b8ee70-ed52-4be0-87c5-414a5d2d2469"
COUNTRY = "americas"
REGION = "NA"

# Base URL for endpoints
BASE_URL = f"https://{COUNTRY}.api.riotgames.com"

# Empty lists to store data
GAME_LIST = []
TIMELINE = []

def process_match_json(match_json, puuid):
    side_dict = {
        100:'blue',
        200:'red'
    }

    try:
        info = match_json['info']


        metadata = match_json['metadata']
        matchId = metadata['matchId']
        participants = metadata['participants']

        player = info['participants'][participants.index(puuid)]

        gameCreation = info['gameCreation']
        gameStartTimestamp = info['gameStartTimestamp']
        gameEndTimestamp = info['gameEndTimestamp']
        timePlayed = (gameEndTimestamp-gameStartTimestamp)/1000
        gameMode = info['gameMode']
        gameVersion = info['gameVersion']
        platformId = info['platformId']
        queueId = info['queueId']
        puuid = player['puuid']
        riotIdGameName = player['summonerName']
        try:
            riotIdTagLine = player['riotIdTagline']
        except:
            riotIdTagLine = ''
        side = side_dict[player['teamId']]
        win = player['win']

        champion = player['championName']
        kills = player['kills']
        deaths = player['deaths']
        assists = player['assists']
        summOne = player['summoner1Id']
        summTwo = player['summoner2Id']
        earlySurrender = player['gameEndedInEarlySurrender']
        surrender = player['gameEndedInSurrender']
        firstBlood = player['firstBloodKill']
        firstBloodAssist = player['firstBloodAssist']
        firstTower = player['firstTowerKill']
        firstTowerAssist = player['firstTowerAssist']
        dragonKills = player['dragonKills']

        damageDealtToBuildings = player['damageDealtToBuildings']
        damageDealtToObjectives = player['damageDealtToObjectives']
        damageSelfMitigated = player['damageSelfMitigated']
        goldEarned = player['goldEarned']
        teamPosition = player['teamPosition']
        lane = player['lane']
        largestKillingSpree = player['largestKillingSpree']
        longestTimeSpentLiving = player['longestTimeSpentLiving']
        objectivesStolen = player['objectivesStolen']
        totalMinionsKilled = player['totalMinionsKilled']
        totalAllyJungleMinionsKilled = player['totalAllyJungleMinionsKilled']
        totalEnemyJungleMinionsKilled = player['totalEnemyJungleMinionsKilled']
        totalNeutralMinionsKilled = totalAllyJungleMinionsKilled + totalEnemyJungleMinionsKilled
        totalDamageDealtToChampions = player['totalDamageDealtToChampions']
        totalDamageShieldedOnTeammates = player['totalDamageShieldedOnTeammates']
        totalHealsOnTeammates = player['totalHealsOnTeammates']
        totalDamageTaken = player['totalDamageTaken']
        totalTimeCCDealt = player['totalTimeCCDealt']
        totalTimeSpentDead = player['totalTimeSpentDead']
        turretKills = player['turretKills']
        turretsLost = player['turretsLost']
        visionScore = player['visionScore']
        controlWardsPlaced = player['detectorWardsPlaced']
        wardsKilled = player['wardsKilled']
        wardsPlaced = player['wardsPlaced']

        item0 = player['item0']
        item1 = player['item1']
        item2 = player['item2']
        item3 = player['item3']
        item4 = player['item4']
        item5 = player['item5']
        item6 = player['item6']

        perks = player['perks']

        perkKeystone = perks['styles'][0]['selections'][0]['perk']
        perkPrimaryRow1 = perks['styles'][0]['selections'][1]['perk']
        perkPrimaryRow2 = perks['styles'][0]['selections'][2]['perk']
        perkPrimaryRow3 = perks['styles'][0]['selections'][3]['perk']
        perkPrimaryStyle = perks['styles'][0]['style']
        perkSecondaryRow1 = perks['styles'][1]['selections'][0]['perk']
        perkSecondaryRow2 = perks['styles'][1]['selections'][1]['perk']
        perkSecondaryStyle = perks['styles'][1]['style']
        perkShardDefense = perks['statPerks']['defense']
        perkShardFlex = perks['statPerks']['flex']
        perkShardOffense = perks['statPerks']['offense']


        matchDF = pd.DataFrame({
            'match_id': [matchId],
            'participants': [participants],
            'game_creation': [gameCreation],
            'game_start_timestamp': [gameStartTimestamp],
            'game_end_timestamp': [gameEndTimestamp],
            'game_version': [gameVersion],
            'queue_id': [queueId],
            'game_mode': [gameMode],
            'platform_id': [platformId],
            'puuid': [puuid],
            'riot_id': [riotIdGameName],
            'riot_tag': [riotIdTagLine],
            'time_played': [timePlayed],
            'side': [side],
            'win': [win],
            'team_position': [teamPosition],
            'lane': [lane],
            'champion': [champion],
            'kills': [kills],
            'deaths': [deaths],
            'assists': [assists],
            'summoner1_id': [summOne],
            'summoner2_id': [summTwo],
            'gold_earned': [goldEarned],
            'total_minions_killed': [totalMinionsKilled],
            'total_neutral_minions_killed': [totalNeutralMinionsKilled],
            'total_ally_jungle_minions_killed': [totalAllyJungleMinionsKilled],
            'total_enemy_jungle_minions_killed': [totalEnemyJungleMinionsKilled],
            'early_surrender': [earlySurrender],
            'surrender': [surrender],
            'first_blood': [firstBlood],
            'first_blood_assist': [firstBloodAssist],
            'first_tower': [firstTower],
            'first_tower_assist': [firstTowerAssist],
            'damage_dealt_to_buildings': [damageDealtToBuildings],
            'turret_kills': [turretKills],
            'turrets_lost': [turretsLost],
            'damage_dealt_to_objectives': [damageDealtToObjectives],
            'dragonKills': [dragonKills],
            'objectives_stolen': [objectivesStolen],
            'longest_time_spent_living': [longestTimeSpentLiving],
            'largest_killing_spree': [largestKillingSpree],
            'total_damage_dealt_champions': [totalDamageDealtToChampions],
            'total_damage_taken': [totalDamageTaken],
            'total_damage_self_mitigated': [damageSelfMitigated],
            'total_damage_shielded_teammates': [totalDamageShieldedOnTeammates],
            'total_heals_teammates': [totalHealsOnTeammates],
            'total_time_crowd_controlled': [totalTimeCCDealt],
            'total_time_spent_dead': [totalTimeSpentDead],
            'vision_score': [visionScore],
            'wards_killed': [wardsKilled],
            'wards_placed': [wardsPlaced],
            'control_wards_placed': [controlWardsPlaced],
            'item0': [item0],
            'item1': [item1],
            'item2': [item2],
            'item3': [item3],
            'item4': [item4],
            'item5': [item5],
            'item6': [item6],
            'perk_keystone': [perkKeystone],
            'perk_primary_row_1': [perkPrimaryRow1],
            'perk_primary_row_2': [perkPrimaryRow2],
            'perk_primary_row_3': [perkPrimaryRow3],
            'perk_secondary_row_1': [perkSecondaryRow1],
            'perk_secondary_row_2': [perkSecondaryRow2],
            'perk_primary_style': [perkPrimaryStyle],
            'perk_secondary_style': [perkSecondaryStyle],
            'perk_shard_defense': [perkShardDefense],
            'perk_shard_flex': [perkShardFlex],
            'perk_shard_offense': [perkShardOffense],
        })
    
        return matchDF
    except:
        return pd.DataFrame()
    

def get_participant_data(match):

    stats = {}
    stats["match_id"] = str(match_id)

    for num, participant in enumerate(participants):
        num = str(num)

        # Participant information
        participant_info = participant["participantId"]
        participant_stats = participant["stats"]

        # Get summoner name using participant ID (separate API call)
        summoner_url = f"{BASE_URL}/lol/summoner/v4/summoners/{participant_info}"
        headers = {'X-Riot-Token': API_KEY}
        summoner_response = requests.get(summoner_url, headers=headers).json()
        summoner_name = summoner_response["name"]

        # Store data
        stats["summoner_" + num] = summoner_name
        stats["champion_" + num] = participant["championName"]
        stats["kills_" + num] = participant_stats["kills"]
        stats["assist_" + num] = participant_stats["assists"]
        stats["deaths_" + num] = participant_stats["deaths"]
        stats["kda_ratio_" + num] = round(participant_stats["kills"] / (participant_stats["deaths"] + 1), 2)
        stats["total_damage_dealt_" + num] = participant_stats["totalDamageDealt"]
        stats["champion_damage_dealt_" + num] = participant_stats["totalDamageDealtToChampions"]
        stats["creep_score_" + num] = participant_stats["totalMinionsKilled"]  # Assuming totalMinionsKilled refers to creep score
        stats["vision_score_" + num] = participant_stats["visionScore"]

        # Items (assuming 6 item slots)
        p_items = []
        for i in range(6):
            try:
                item_id = participant_stats["items"][i]["itemId"]
                item_url = f"https://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/item.json"
                item_response = requests.get(item_url).json()
                item_name = item_response["data"][str(item_id)]["name"]
                p_items.append(item_name)
            except (KeyError, requests.exceptions.RequestException):
                p_items.append("None")
        stats["items_" + num] = p_items

        # Placeholder for get_timeline_data(match_id) - Implement if needed
        # timeline_data = get_timeline_data(match_id)
        # ... (process timeline data)

    return stats

def get_timeline_data(match_id):
    timeline_url = f"{BASE_URL}/lol/match/v5/matches/{match_id}/timeline"
    headers = {'X-Riot-Token': API_KEY}

    try:
        timeline_response = requests.get(timeline_url, headers=headers).json()
        frames = timeline_response["info"]["frames"]
        timeline_data = []

        for index, frame in enumerate(frames):
            frame_data = {"frame": index}
            for participant_id, participant_data in frame["participantFrames"].items():
                participant_data = {"participantId": participant_id, **participant_data}
                frame_data[f"participant_{participant_id}"] = participant_data

                # Extract desired data
                cs = participant_data.get("creepScore", 0)
                xp = participant_data.get("experience", 0)
                gold = participant_data.get("currentGold", 0)
                totalgold = participant_data.get("goldEarned", 0)
                level = participant_data.get("level", 0)
                neutralminions = participant_data.get("neutralMinionsKilled", 0)

                # Store data (similar to your previous approach)
                frame_data[f"cs_{participant_id}"] = cs
                frame_data[f"xp_{participant_id}"] = xp
                frame_data[f"gold_{participant_id}"] = gold
                frame_data[f"totalgold_{participant_id}"] = totalgold
                frame_data[f"level_{participant_id}"] = level
                frame_data[f"neutralminions_{participant_id}"] = neutralminions

            TIMELINE.append(frame_data)

        return timeline_data

    except (requests.exceptions.RequestException, KeyError):
        print(f"Error retrieving timeline data for match {match_id}")
        return None

def graph_totgold(TIMELINE):
    plt.plot(TIMELINE['frame'], TIMELINE['totalgold_1'], label='Player 1 Total Gold')
    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Gold')
    plt.title('Player 1 Total Gold Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()  
    
def get_name_from_puuid(puuid):
    name_url = f'https://{COUNTRY}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    headers = {'X-Riot-Token': API_KEY}
    name_rsp = requests.get(name_url, headers=headers).json()
    print(name_rsp)
    gameName = name_rsp["gameName"]
    tagLine = name_rsp["tagLine"]
    name = gameName+"#"+str(tagLine)
    return gameName, tagLine, name


    
def generate_dmg_graph(match_details):
    for index, match in match_details.iterrows():
        numstr = "0123456789"
        yaxis = []
        xaxis = []
        for num in numstr:
            playerdmg = match["champion_damage_dealt_" + num]
            champ = match["champion_"+num]
            yaxis.append(playerdmg)
            xaxis.append(champ)
        plt.bar(xaxis, yaxis)
        plt.xlabel('Champion')
        plt.ylabel('Damage Dealt to Champions')
        plt.title('Damage Dealt by Each Player')
        plt.savefig(f'static/dmggraph_{match["match_id"]}.png')
        plt.close()
    return

def get_name_from_puuid(puuid):
    name_url = f'https://{COUNTRY}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    headers = {'X-Riot-Token': API_KEY}
    name_rsp = requests.get(name_url, headers=headers).json()

    gameName = name_rsp["gameName"]
    tagLine = name_rsp["tagLine"]
    name = gameName+"#"+str(tagLine)
    return gameName, tagLine, name

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
        summoner_name = get_name_from_puuid(puuid)
        # Make the HTTP GET request to the Riot Games API to get match list
        match_list_response = requests.get(match_list_url, headers=headers)
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
    match_details = None

    if request.method == 'POST':
        puuid = request.form['puuid']
        if puuid:
            summoner_name, profile_icon_id, matches = get_summoner_data_by_puuid(puuid)  # Update function call to get profile_icon_id
            match_details = get_summoner_data_by_puuid(puuid) 
            
            generate_dmg_graph(match_details)
    if match_details is None:
        match_details = pd.DataFrame()
    return render_template('index.html', summoner_name=summoner_name, profile_icon_url=profile_icon_url, match_details=match_details)

if __name__ == '__main__':
    app.run(debug=True)