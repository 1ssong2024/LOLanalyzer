import requests
#gold over time graph
import datetime
import cassiopeia as cass
from cassiopeia import Summoner
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

#GAME_LIST = []
MATCHES = 10
COUNTRY = "americas"
REGION = "NA"
API_KEY = "RGAPI-55b37958-a7f3-4ec7-9a09-8ab034536d9f"
cass.set_riot_api_key(API_KEY)
puuid = "9ydrHSXJcdONbjsFEYZIRxZscA4aDXgc8j4UYhwVhnk-LQlI1aGQXXoNorr0CqQ04O1ckPu0KZ4Gpw"
#it woudl make sense to have a dictinoary with 
#the key being match and the val being the dataframe... right?
#TIMELINE = [] 


def greatest_smaller_number_last_index(lst, x):
    smaller_numbers = [idx for idx, num in enumerate(lst) if num <= x]
    if not smaller_numbers:
        return -1  # If there are no smaller numbers in the list
    return max(smaller_numbers)

def get_name_from_puuid(puuid):
    name_url = f'https://{COUNTRY}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    headers = {'X-Riot-Token': API_KEY}
    name_rsp = requests.get(name_url, headers=headers).json()
    # print(name_rsp)
    gameName = name_rsp["gameName"]
    tagLine = name_rsp["tagLine"]
    name = gameName+"#"+str(tagLine)
    return gameName, tagLine, name

def get_participant_data(participants, match):
    stats = {}
    stats["match_id"] = str(match.id)
    plist = summoner_data_json("NA1_"+str(match.id))
    # print(plist)
    for num, p in enumerate(participants):
        num = str(num+1)
        player=p.summoner
        gameName, tagLine, name = get_name_from_puuid(player.puuid)
        stats["summoner_" + num] = name
        stats["champion_" + num] = plist[int(num)-1]
        stats["position_" + num] = p.individual_position.name
        #stats["runes_" + num] = p.runes.keystone.name
        #stats["d_spell_" + num] = p.summoner_spell_d.name
        #stats["f_spell_" + num] = p.summoner_spell_f.name
        stats["kills_" + num] = p.stats.kills
        stats["assist_" + num] = p.stats.assists
        stats["deaths_" + num] = p.stats.deaths
        stats["kda_ratio_" + num] = round(p.stats.kda, 2)
        stats["total_damage_dealt_" + num] = p.stats.total_damage_dealt
        stats["champion_damage_dealt_" + num] = p.stats.total_damage_dealt_to_champions
        stats["creep_score_" + num] = p.stats.total_minions_killed
        stats["vision_score_" + num] = p.stats.vision_score
        
        p_items = []
        #number_of_item_slots = 6
        # for i in range(number_of_item_slots):
        #     try:
        #         p_items.append(p.stats.items[i].name)
        #     except AttributeError:
        #         p_items.append("None")
        stats["items_"+num] = p_items
    return stats

def summoner_data_json(matchid):
    requrl = "https://americas.api.riotgames.com/lol/match/v5/matches/" + matchid
    headers = {'X-Riot-Token': API_KEY }
    
    match_response = requests.get(requrl, headers=headers)

    if match_response.status_code == 200:
        match_data = match_response.json()
        test = match_data["info"]["participants"]
        plist = [player["championName"] for player in test]
        return (plist)

def timeline_json(match_id):
    requrl = "https://americas.api.riotgames.com/lol/match/v5/matches/" + match_id + "/timeline"
    headers = {'X-Riot-Token': API_KEY }
    match_response = requests.get(requrl, headers=headers)

    if match_response.status_code == 200:
        match_data = match_response.json()
        test = match_data["info"]["frames"]
        framelist = [[frame["participantFrames"][player]["damageStats"] for player in frame["participantFrames"]] for frame in test]
        return (framelist)

#dmg = timeline_json("NA1_4957699488")
#print(dmg)

def get_summoner_data_by_puuid(summoner):
    GAME_LIST = []
    matches = summoner.match_history  
    for match in matches[0:MATCHES]:
        mdata = get_participant_data(match.participants, match)
        GAME_LIST.append(mdata)
    match_details = pd.DataFrame(GAME_LIST)
    return summoner.profile_icon.id, match_details

def get_timeline_data(gamenum, puuid, region):
    #global TIMELINE
    summoner = Summoner(puuid=puuid, region=region)

    match_history = summoner.match_history
    match = match_history[gamenum]
    print("Match ID:", match.id)
    
    # print("Frame interval:", match.timeline.frame_interval)
    # The cumulative timeline property allows you to get some info about participants during the match.
    #  You access the cumulative timeline by providing the duration into the game that you want the info for.
    #  In this case, we're accessing the game at 15 minutes and 30 seconds.
    #  Some data is only available every one minute.
    playersandkills = [] #list of lists, sech sublist corr tp a player + when they got the kill
    #use seconds in p.timeline.
    timeline = match.timeline.frames
    TIMELINE = []
    print(match.id)
    dmgstats = timeline_json("NA1_"+str(match.id))
    for player in match.participants:
        playerlist=[-1]
        for index, kill in enumerate(player.timeline.champion_kills): #for each player, store a list of times they got a kill
            playerlist.append(kill.timestamp.seconds//60) #participant, killlist
        playersandkills.append(playerlist)
    for index,frame in enumerate(timeline): #each frame is a minute
        frame1dmg = dmgstats[index]
        #print(frame.participant_frames)
        framedct = {}
        framedct["frame"] = index
        red_teamgold = 0
        blue_teamgold = 0
        red_teamdmg = 0
        blue_teamdmg = 0
        for participant in frame.participant_frames: #participant 1-10
            dmg = frame1dmg[participant-1]["totalDamageDoneToChampions"]
            dmgtaken = frame1dmg[participant-1]["totalDamageTaken"]
            cs = frame.participant_frames[participant].creep_score
            xp = frame.participant_frames[participant].experience
            gold = frame.participant_frames[participant].current_gold
            totalgold = frame.participant_frames[participant].gold_earned
            level = frame.participant_frames[participant].level
            neutralminions = frame.participant_frames[participant].neutral_minions_killed
            #champion = match.participants[participant].champion
            if participant in range (1,6): red_teamgold += totalgold 
            if participant in range(6,11): blue_teamgold += totalgold
            if participant in range (1,6): red_teamdmg += dmg 
            if participant in range(6,11): blue_teamdmg += dmg
            participant = str(participant)
            #framedct[participant] = champion
            framedct["dmg_"+participant] = dmg
            framedct["dmgtaken_"+participant] = dmgtaken
            framedct["cs_"+participant] = cs #average cs.min of winning/losing team
            framedct["xp_"+participant] = xp #average xp/min for winning/losing team
            framedct["gold_"+participant] = gold #for kills/min, colorcode whol dies based on player
            framedct["totalgold_"+participant] = totalgold #each placer contribution to totalgold (contribution to totalgold vs contribution to dmg)
            framedct["level_"+participant] = level
            framedct["neutralminions_"+participant] = neutralminions
            framedct["kills_"+participant] = greatest_smaller_number_last_index(playersandkills[int(participant)-1],index)
        framedct["totalgold_red"] = red_teamgold
        framedct["totalgold_blue"] = blue_teamgold
        framedct["totaldmg_red"] = red_teamdmg
        framedct["totaldmg_blue"] = blue_teamdmg
        TIMELINE.append(framedct)
    #p = match.participants[summoner] #this has a bunch of stuff
    TIMELINE = pd.DataFrame(TIMELINE)
    return TIMELINE

#contribution to totalgold
def graph_goldcontr(TIMELINE, GAME_LIST, matchind):
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        #print(GAME_LIST.at[matchind,"champion_"+player])
        # print(TIMELINE['totalgold_' + player])
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        plt.plot(TIMELINE['frame'], TIMELINE['totalgold_'+str(player)]/TIMELINE['totalgold_red' if int(player)<6 else 'totalgold_blue'], label=GAME_LIST.at[matchind,"champion_"+player] + ' Total Gold', color=color, marker=marker, markersize=markersize)

    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Gold')
    plt.title('Total Gold Contribution of All Players Over Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/goldcontr_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_dmgcontr(TIMELINE, GAME_LIST, matchind):
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        #print(GAME_LIST.at[matchind,"champion_"+player])
        # print(TIMELINE['totalgold_' + player])
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        plt.plot(TIMELINE['frame'], TIMELINE['dmg_'+str(player)]/TIMELINE['totaldmg_red' if int(player)<6 else 'totaldmg_blue'], label=GAME_LIST.at[matchind,"champion_"+player] + ' Total Damage', color=color, marker=marker, markersize=markersize)

    plt.xlabel('Time (Minute)')
    plt.ylabel('Proportion of Total Damage')
    plt.title('Total Damage Dealt Contribution of All Players Over Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/dmgcontr_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_dmgdealt(TIMELINE, GAME_LIST, matchind):
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        #print(GAME_LIST.at[matchind,"champion_"+player])
        # print(TIMELINE['totalgold_' + player])
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        plt.plot(TIMELINE['frame'], TIMELINE['dmg_'+str(player)], label=GAME_LIST.at[matchind,"champion_"+player] + ' Total Damage', color=color, marker=marker, markersize=markersize)

    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Damage Dealt')
    plt.title('Total Damage Dealt of All Players Over Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/dmgdealt_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_dmgtaken(TIMELINE, GAME_LIST, matchind):
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        #print(GAME_LIST.at[matchind,"champion_"+player])
        # print(TIMELINE['totalgold_' + player])
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        plt.plot(TIMELINE['frame'], TIMELINE['dmgtaken_'+str(player)], label=GAME_LIST.at[matchind,"champion_"+player] + ' Total Damage', color=color, marker=marker, markersize=markersize)

    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Damage Taken')
    plt.title('Total Damage Taken of All Players Over Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/dmgtaken_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_xp(TIMELINE, GAME_LIST, matchind):
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        plt.plot(TIMELINE['frame'], TIMELINE['xp_' + player], label=GAME_LIST.at[matchind,"champion_"+player] + ' Experience')

    plt.xlabel('Time (Minute)')
    plt.ylabel('Experience')
    plt.title('Experience of All Players Over Time')
    plt.legend()
    plt.grid(True)
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left')
    plt.savefig(f'static/experience_player_{player}.png')
    plt.show()

def graph_xp_rb(TIMELINE, GAME_LIST, matchind):
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players

    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for i, player in enumerate(players):
        champion = GAME_LIST.at[matchind, "champion_" + player]
        xp = TIMELINE['xp_' + player]
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        position = GAME_LIST.at[matchind, "position_" + player]
        marker_label = position[0]  # First letter of the position
        plt.plot(TIMELINE['frame'], xp, label=champion + ' Experience', color=color, marker=marker, markersize=markersize)
        plt.text(TIMELINE['frame'].iloc[-1], xp.iloc[-1], marker_label, color=color, ha='right', va='center')  # Add text label next to the last point

    plt.xlabel('Time (Minute)')
    plt.ylabel('Experience')
    plt.title('Experience of All Players Over Time')
    plt.legend()
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/xp_rb_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_totgold_rb(TIMELINE, GAME_LIST, matchind):
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players

    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for i, player in enumerate(players):
        champion = GAME_LIST.at[matchind, "champion_" + player]
        total_gold = TIMELINE['totalgold_' + player]
        position = GAME_LIST.at[matchind, "position_" + player]
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        # marker_label = position[0]  # First letter of the position
        plt.plot(TIMELINE['frame'], total_gold, label=champion + ' Total Gold', color=color, marker=marker, markersize=markersize)
        #  plt.text(TIMELINE['frame'].iloc[-1], total_gold.iloc[-1], marker_label, color=color, ha='right', va='center')  # Add text label next to the last point

    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Gold')
    plt.title('Total Gold of All Players Over Time')
    plt.legend()
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/totgold_rb_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def graph_cs(TIMELINE, GAME_LIST, matchind):
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    # Plotting total gold for all players over time
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for player in players:
        #print("champion_"+player)
        plt.plot(TIMELINE['frame'], TIMELINE['cs_' + player], label=GAME_LIST.at[matchind,"champion_"+player] + ' CS')

    plt.xlabel('Time (Minute)')
    plt.ylabel('CS')
    plt.title('CS of All Players Over Time')
    plt.legend()
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/cs_player_{player}.png')
    plt.show()

def graph_cs_rb(TIMELINE, GAME_LIST, matchind):
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players

    plt.figure(figsize=(10, 6))  # Adjust figure size if needed
    for i, player in enumerate(players):
        champion = GAME_LIST.at[matchind, "champion_" + player]
        cs = TIMELINE['cs_' + player]
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 5
        position = GAME_LIST.at[matchind, "position_" + player]
        marker_label = position[0]  # First letter of the position
        plt.plot(TIMELINE['frame'], cs, label=champion + ' CS', color=color, marker=marker, markersize=markersize)
        plt.text(TIMELINE['frame'].iloc[-1], cs.iloc[-1], marker_label, color=color, ha='right', va='center')  # Add text label next to the last point

    plt.xlabel('Time (Minute)')
    plt.ylabel('CS')
    plt.title('CS of All Players Over Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.savefig(f'static/cs_rb_{GAME_LIST.at[matchind,"match_id"]}.png')
    plt.show()

def xp_v_gold(TIMELINE, GAME_LIST, player):
    # Plotting the actual points as scatter plot
    x = TIMELINE["totalgold_" + player]
    y = TIMELINE["xp_" + player]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    regression_line = slope * x + intercept
    plt.scatter(x,y)
    plt.plot(x, regression_line, color='red', label='Regression Line')

    # Putting labels
    plt.xlabel('Total Gold')
    plt.ylabel('XP')
    plt.title('Gold vs XP for ')
    plt.savefig(f'static/gold_vs_xp_player_{player}.png')
    plt.show()


def plot_xp_vs_gold_reg(TIMELINE, GAME_LIST, matchind):
    plt.figure(figsize=(10, 6))
    red_colors = plt.cm.Reds(np.linspace(0.4, 1, 5))  # Different shades of red for red team players
    blue_colors = plt.cm.Blues(np.linspace(0.4, 1, 5))  # Different shades of blue for blue team players
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    for player in players:
        x = TIMELINE["xp_" + player]
        y = TIMELINE["totalgold_" + player]
        team = 'red' if int(player) <= 5 else 'blue'
        color = red_colors[int(player) - 1] if team == 'red' else blue_colors[int(player) - 6]
        marker = 'o' if team == 'red' else 's'
        markersize = 20
        plt.scatter(x, y, label=GAME_LIST.at[matchind,"champion_"+player] + ' XP v Gold', color=color, marker=marker, s=markersize)
    blue_x = [xp for num in range(6,11) for xp in TIMELINE["xp_" + str(num)]]
    blue_y = [gold for num in range(6,11) for gold in TIMELINE["totalgold_" + str(num)]]
    red_x = [xp for num in range(1,6) for xp in TIMELINE["xp_" + str(num)]]
    red_y = [gold for num in range(1,6) for gold in TIMELINE["totalgold_" + str(num)]]
    blue_slope, blue_intercept, blue_r_value, blue_p_value, blue_std_err = stats.linregress(blue_x, blue_y)
    red_slope, red_intercept, red_r_value, red_p_value, red_std_err = stats.linregress(red_x, red_y)
    red_regression_line = red_slope * np.array(red_x) + red_intercept
    blue_regression_line = blue_slope * np.array(blue_x) + blue_intercept
    
    plt.plot(blue_x, blue_regression_line, label=f'Blue Team Regression Line: y = {blue_slope:.2f}x + {blue_intercept:.2f}',color="blue")
    plt.plot(red_x, red_regression_line, label=f'Red Team Regression Line: y = {red_slope:.2f}x + {red_intercept:.2f}',color="red")
    # Putting labels
    plt.xlabel('Total XP')
    plt.ylabel('Gold')
    plt.title('XP v Gold for All Players')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75)
    plt.grid(True)
    plt.savefig(f'static/xp_vs_gold_reg{player}.png')
    plt.show()

#cs and kills v gold regline
def plot_cs_and_kills_v_gold(TIMELINE):
    plt.figure(figsize=(10, 8))
    for player in range(1, 11):
        X1 = np.array(TIMELINE["cs_" + str(player)])
        X2 = np.array(TIMELINE["kills_" + str(player)])
        y = np.array(TIMELINE["totalgold_" + str(player)])

        # Reshape X1 and X2 for sklearn input
        X = np.column_stack((X1, X2))

        # Fit the regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict values
        y_pred = model.predict(X)

        # Plot regression line for X1
        plt.scatter(X1, y, color='red', label=f'Player {player} CS')
        plt.plot(X1, y_pred, label=f'Player {player} Regression line (CS)')

        # Plot regression line for X2
        plt.scatter(X2, y, color='blue', label=f'Player {player} Kills')
        plt.plot(X2, y_pred, label=f'Player {player} Regression line (Kills)')

    plt.xlabel('CS / Kills')
    plt.ylabel('Total Gold')
    plt.title('Regression Analysis for CS, Kills vs Total Gold Earned')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.subplots_adjust(right=0.75) 
    plt.grid(True)
    plt.show()


def generate_dmg_graph(GAME_LIST, gamenum):
    plt.figure(figsize=(10, 6))
    game = GAME_LIST.iloc[gamenum]
    numstr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    yaxis = []
    xaxis = []
    for num in numstr:
        playerdmg = game["champion_damage_dealt_" + num]
        champ = game["champion_"+num]
        yaxis.append(playerdmg)
        xaxis.append(champ)
    colors = ['#FF9999' if int(num) <= 5 else '#99CCFF' for num in numstr]  # Shades of red and blue
    plt.bar(xaxis, yaxis, color=colors) 
    plt.xlabel('Player')
    plt.xticks(rotation='vertical')
    plt.ylabel('Damage Dealt to Champions')
    plt.title('Damage Dealt by Each Player')
    plt.savefig(f'static/dmggraph_{game["match_id"]}.png')
    plt.show()
    return

'''
if __name__ == "__main__":
    puuid = "9ydrHSXJcdONbjsFEYZIRxZscA4aDXgc8j4UYhwVhnk-LQlI1aGQXXoNorr0CqQ04O1ckPu0KZ4Gpw"
    summoner = Summoner(puuid=puuid, region=REGION)
    profile_icon_id, GAME_LIST = get_summoner_data_by_puuid(summoner) 
    get_timeline_data(puuid, region="NA")
    graph_goldcontr(TIMELINE, GAME_LIST, 0)
    graph_dmgcontr(TIMELINE, GAME_LIST, 0)
    graph_dmgdealt(TIMELINE, GAME_LIST, 0)
    graph_dmgtaken(TIMELINE, GAME_LIST, 0)
    generate_dmg_graph(GAME_LIST)
    # graph_totgold(TIMELINE, 0)
    # graph_totgold_rb(TIMELINE, 0)
    # graph_xp(TIMELINE, 0)
    # graph_xp_rb(TIMELINE, 0)
    # graph_cs(TIMELINE, 0)
    # graph_cs_rb(TIMELINE, 0)
    players = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    plot_xp_vs_gold_reg(TIMELINE, 0)
    plot_cs_and_kills_v_gold(TIMELINE)
    # Plotting gold vs XP for each player
    # for player in players:
    #     xp_v_gold(TIMELINE, player)
'''
'''
puuid = '9ydrHSXJcdONbjsFEYZIRxZscA4aDXgc8j4UYhwVhnk-LQlI1aGQXXoNorr0CqQ04O1ckPu0KZ4Gpw'

gameName, tagLine, summoner_name = get_name_from_puuid(puuid) 
summoner = Summoner(puuid=puuid, region=REGION)
profile_icon_id, match_details = get_summoner_data_by_puuid(summoner) #match details is summary stats where each line= one game
if summoner_name:
    profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/10.25.1/img/profileicon/{profile_icon_id}.png'
for i in range(2):
    timeline = get_timeline_data(i, puuid, "NA")
    generate_dmg_graph(match_details, i)
    graph_goldcontr(timeline, match_details, i)
    graph_dmgcontr(timeline, match_details, i)
    graph_dmgdealt(timeline, match_details, i)
    graph_dmgtaken(timeline, match_details, i)
'''

#'''
@app.route('/', methods=['GET', 'POST'])
def index():
    summoner_name = None
    profile_icon_url = None
    match_details = None

    if request.method == 'POST':
        puuid = request.form['puuid']
        if puuid:
            gameName, tagLine, summoner_name = get_name_from_puuid(puuid) 
            summoner = Summoner(puuid=puuid, region=REGION)
            profile_icon_id, match_details = get_summoner_data_by_puuid(summoner) #match details is summary stats where each line= one game
            if summoner_name:
                profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/10.25.1/img/profileicon/{profile_icon_id}.png'
            for i in range(MATCHES):
                timeline = get_timeline_data(i, puuid, "NA")
                generate_dmg_graph(match_details, i)
                graph_dmgdealt(timeline, match_details, i)
                graph_dmgcontr(timeline, match_details, i)
                graph_dmgtaken(timeline, match_details, i)
                graph_goldcontr(timeline, match_details, i)
                graph_totgold_rb(timeline, match_details, i)
                graph_xp_rb(timeline, match_details, i)
                graph_cs_rb(timeline, match_details, i)
    if match_details is None:
        match_details = pd.DataFrame()
    return render_template('index.html', summoner_name=summoner_name, profile_icon_url=profile_icon_url, match_details=match_details)

if __name__ == '__main__':
    app.run(debug=True)

#'''