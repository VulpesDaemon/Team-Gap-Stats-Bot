#!/bin/python3

import requests
import sys
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Google Vars
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('gaptest-342721-88a00ca5760a.json', scope)
client = gspread.authorize(creds)

region = 'NA1'
apikey = 'RGAPI-'
gameID = ''
redID = 200
blueID = 100

with open('championIdKey.json') as f:
    champ_ids = json.load(f)

with open('itemIdKey.json') as f:
    item_ids = json.load(f)

def getChamp(champID: int):
    return champ_ids[str(champID)]

def getItem(itemID: int):
    return item_ids[str(itemID)]

def main():
    
    # Initial request
    # gameID = sys.argv[1]
    GameRequest = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{region}_{gameID}?api_key={apikey}')
    GameData = GameRequest.json()
    print(str(GameRequest.status_code))

    # Error catching
    if GameRequest.status_code == 404:
        print("Match ID not found")
    if GameRequest.status_code == 403:
        print("Bad API key")
    if GameRequest.status_code == 400:
        print('Incorrect Format')
    if GameRequest.status_code == 429:
        print('Too many requests, try again later')


    ### Match Info ###
    basic_info = {}
    basic_info['Game Duration'] = GameData['info']['gameDuration']
    basic_info['Match ID'] = GameData['info']['gameId']
    basic_info['Version'] = GameData['info']['gameVersion']
    # print(basic_info)

    red_team_objectives = {}
    blue_team_objectives = {}
    
    red_team_bans = {}
    blue_team_bans = {}

    ### Team Data ###
    for team in GameData['info']['teams']:
        team_object = {}
        banlist = []

        for ban in team['bans']:
            banlist.append(getChamp(ban['championId']))

        team_object['Baron Kills'] = team['objectives']['baron']['kills']
        team_object['Rift Herald Kills'] = team['objectives']['riftHerald']['kills']
        team_object['Dragon Kills'] = team['objectives']['dragon']['kills']
        team_object['Tower Kills'] = team['objectives']['tower']['kills']
        team_object['Inhibitor Kills'] = team['objectives']['inhibitor']['kills']
        team_object['Champion Kills'] = team['objectives']['champion']['kills']

        if team['teamId'] == blueID:
            blue_team_objectives = team_object
            blue_team_bans = banlist
        elif team['teamId'] == redID:
            red_team_objectives = team_object
            red_team_bans = banlist
   
    ### Player Data ###
    for participant in GameData['info']['participants']:
        player_data = {}
        player_data['Player'] = participant['summonerName']
        player_data['Role'] = participant['teamPosition']
        if participant['teamPosition'] == "UTILITY": # renaming utility to support
            player_data['Role'] = 'SUPPORT'
        player_data['Champion'] = participant['championName']
        # assigning team for player
        if participant['teamId'] == blueID:
            player_data['Team'] = 'Blue'
        elif participant['teamId'] == redID:
            player_data['Team'] = 'Red'
        else:
            player_data['Team'] = 'N/A'

        ### Player Stats ###
        ## Basic Stats ##
        player_data['Kills'] = participant['kills']
        player_data['Deaths'] = participant['deaths']
        player_data['Assists'] = participant['assists']
        ## Specific Stats ##
        # Damage #
        player_data['Champion Damage'] = participant['totalDamageDealtToChampions']
        player_data['Structure Damage'] = participant['damageDealtToBuildings']
        # Taken and Healed #
        player_data['Damage Healed'] = participant['totalHeal']
        player_data['Damage Shielded'] = participant['totalDamageShieldedOnTeammates']
        player_data['Damage Taken'] = participant['totalDamageTaken']
        player_data['Damage Mitigated'] = participant['damageSelfMitigated']
        # Vision #
        player_data['Vision Score'] = participant['visionScore']
        player_data['Pinks Purchased'] = participant['visionWardsBoughtInGame']
        player_data['Wards Placed'] = participant['wardsPlaced']
        player_data['Wards Destroyed'] = participant['wardsKilled']
        # Gold and Exp #
        player_data['Gold Earned'] = participant['goldEarned']
        player_data['Champion Level'] = participant['champLevel']
        player_data['CS'] = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
        player_data['Minion Kills'] = participant['totalMinionsKilled']
        player_data['Jungle Minion Kills'] = participant['neutralMinionsKilled']
        ## Fun Stats ##
        player_data['Towers Destroyed'] = participant['turretKills']
        player_data['Inhibitors Destroyed'] = participant['inhibitorKills']
        player_data['CC Score'] = participant['timeCCingOthers']
        player_data['Damage per Minute'] = round(participant['challenges']['damagePerMinute'], 2)
        player_data['Gold per Minute'] = round(participant['challenges']['goldPerMinute'], 2)
        player_data['Vision per Minute'] = round(participant['challenges']['visionScorePerMinute'],2)
        player_data['Winner'] = participant['win']
        ## Items ##
        itemlist = []
        for item in range(0,7):
            itemlist.append(getItem(participant[f"item{item}"]))
        player_data['Items'] = itemlist
        ## Runes ##

        # print(player_data)
    
    print(player_data)
    # print(itemlist)

    # print(red_team_bans)
    # print(blue_team_bans)
    # print(red_team_objectives)    
    # print(blue_team_objectives)


if __name__ == '__main__':
    main()
