import requests
from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cassiopeia as cass
from cassiopeia import Summoner

app = Flask(__name__)

COUNTRY = "americas"
REGION = "NA"
API_KEY = "RGAPI-b8b8ee70-ed52-4be0-87c5-414a5d2d2469"
cass.set_riot_api_key(API_KEY)
GAME_LIST = []
TIMELINE = [] #based on match ID (not a global... need for other matches as well :)

def get_timeline_data(match):
    timeline = match.timeline.frames
    for index,frame in enumerate(timeline): #each frame is a minute
        #print(frame.participant_frames)
        framedct = {}
        framedct["frame"] = index
        for participant in frame.participant_frames: #participant 1-10
            cs = frame.participant_frames[participant].creep_score
            xp = frame.participant_frames[participant].experience
            gold = frame.participant_frames[participant].current_gold
            totalgold = frame.participant_frames[participant].gold_earned
            level = frame.participant_frames[participant].level
            neutralminions = frame.participant_frames[participant].neutral_minions_killed
            participant = str(participant)
            framedct["cs_"+participant] = cs
            framedct["xp_"+participant] = xp
            framedct["gold_"+participant] = gold
            framedct["totalgold_"+participant] = totalgold
            framedct["level_"+participant] = level
            framedct["neutralminions_"+participant] = neutralminions
        TIMELINE.append(framedct)
    TIMELINE = pd.DataFrame(TIMELINE)
    graph_totgold(TIMELINE)
    return TIMELINE
        
def graph_totgold(TIMELINE):
    plt.plot(TIMELINE['frame'], TIMELINE['totalgold_1'], label='Player 1 Total Gold')
    plt.xlabel('Time (Minute)')
    plt.ylabel('Total Gold')
    plt.title('Player 1 Total Gold Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()    

def get_participant_data(participants, match):
    stats = {}
    stats["match_id"] = str(match.id)
    for num, p in enumerate(participants):
        num = str(num)
        player=p.summoner
        gameName, tagLine, name = get_name_from_puuid(player.puuid)
        stats["summoner_" + num] = name
        #stats["champion_" + num] = p.champion.name
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


def get_name_from_puuid(puuid):
    name_url = f'https://{COUNTRY}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    headers = {'X-Riot-Token': API_KEY}
    name_rsp = requests.get(name_url, headers=headers).json()
    print(name_rsp)
    gameName = name_rsp["gameName"]
    tagLine = name_rsp["tagLine"]
    name = gameName+"#"+str(tagLine)
    return gameName, tagLine, name


def get_summoner_data_by_puuid(summoner):
    GAME_LIST.clear()
    TIMELINE.clear()
    matches = summoner.match_history  
    for match in matches[0:2]:
        print(match)
        mdata = get_participant_data(match.participants, match)
        GAME_LIST.append(mdata)
    match_details = pd.DataFrame(GAME_LIST)
    print(match_details)
    return summoner.profile_icon.id, match_details


def generate_dmg_graph(match_details):
    for index, match in match_details.iterrows():
        numstr = "0123456789"
        yaxis = []
        xaxis = []
        for num in numstr:
            playerdmg = match["champion_damage_dealt_" + num]
            champ = "Player_" + num
            yaxis.append(playerdmg)
            xaxis.append(champ)
        plt.bar(xaxis, yaxis)
        plt.xlabel('Player')
        plt.ylabel('Damage Dealt to Champions')
        plt.title('Damage Dealt by Each Player')
        plt.savefig(f'static/dmggraph_{match["match_id"]}.png')
        plt.close()
    return


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
            profile_icon_id, match_details = get_summoner_data_by_puuid(summoner) 
            if summoner_name:
                profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/10.25.1/img/profileicon/{profile_icon_id}.png'
            generate_dmg_graph(match_details)
    if match_details is None:
        match_details = pd.DataFrame()
    return render_template('index.html', summoner_name=summoner_name, profile_icon_url=profile_icon_url, match_details=match_details)

if __name__ == '__main__':
    app.run(debug=True)