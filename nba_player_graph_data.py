import pandas as pd
import numpy as np
import argparse
import itertools
import time
from tqdm import tqdm

from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import playerdashptshots, playerdashptpass, playerdashptshotdefend, playerdashptreb, playerdashboardbylastngames, playergamelog, leaguegamefinder, commonallplayers

def getAllPlayers(season):

    nba_teams = teams.get_teams()
    nba_players = players.get_players()
    all_players = commonallplayers.CommonAllPlayers(season=season).get_data_frames()[0]

    return nba_teams, all_players

def getTeamPlayers(nba_teams, all_players, team):

    team_id = [x['id'] for x in nba_teams if x['nickname']==args['team']][0]
    team_players = all_players[all_players['TEAM_ID'] == team_id]
    team_players = team_players[['TEAM_ID', 'PERSON_ID', 'DISPLAY_LAST_COMMA_FIRST']].values.tolist()

    return team_players, team_id

def getSeasonGames(team_id, season):

    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    games = gamefinder.get_data_frames()[0]
    season_games = games[games.SEASON_ID.str[-4:]==season[:4]]

    return season_games

def createGameDateTuples(season_games):

    game_dates = []
    for game_id in season_games['GAME_ID'].unique():
        game_dates.append((game_id, season_games[season_games['GAME_ID']==game_id]['GAME_DATE'].values[0]))

    return game_dates

def collectPlayerData(team_players, game_dates, team_id, season):

    players = [x[1] for x in team_players]

    players_dict = {}
    for p_id in tqdm(players):
        p_df_dict = {}
        for g_id,g_date in game_dates:
            try:
                passes = playerdashptpass.PlayerDashPtPass(team_id=team_id, player_id=p_id, season=season, per_mode_simple='Totals', date_to_nullable=g_date, date_from_nullable=g_date)
                time.sleep(1)

                passes_df = passes.get_data_frames()[0]
                if passes_df.empty:
                    passes_df['PLAYER_ID'] = p_id

                passes_df['GAME_ID'] = g_id
                passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {p_id}, Game {g_id} resulted in an error for passes api")
                passes_df = pd.DataFrame([[p_id, g_id]], columns=['PLAYER_ID', 'GAME_ID'])
                passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])

            try:
                shots = playerdashptshots.PlayerDashPtShots(team_id=team_id, player_id=p_id, season=season, per_mode_simple='Totals', date_to_nullable=g_date, date_from_nullable=g_date)
                time.sleep(1)

                shots_df = shots.get_data_frames()[4]
                if shots_df.empty:
                    shots_df['PLAYER_ID'] = p_id

                shots_df['GAME_ID'] = g_id
                shots_df = shots_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {p_id}, Game {g_id} resulted in an error for shots api")
                shots_df = pd.DataFrame([[p_id, g_id]], columns=['PLAYER_ID', 'GAME_ID'])
                shots_df = shots_df.set_index(['GAME_ID', 'PLAYER_ID'])

            try:
                rebs = playerdashptreb.PlayerDashPtReb(team_id=team_id, player_id=p_id, season=season, per_mode_simple='Totals', date_to_nullable=g_date, date_from_nullable=g_date)
                time.sleep(1)

                rebs_df = rebs.get_data_frames()[1]
                if rebs_df.empty:
                    rebs_df['PLAYER_ID'] = p_id

                rebs_df['GAME_ID'] = g_id
                rebs_df = rebs_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {p_id}, Game {g_id} resulted in an error for rebounds api")
                rebs_df = pd.DataFrame([[p_id, g_id]], columns=['PLAYER_ID', 'GAME_ID'])
                rebs_df = rebs_df.set_index(['GAME_ID', 'PLAYER_ID'])

            try:
                defense = playerdashptshotdefend.PlayerDashPtShotDefend(team_id=team_id, player_id=p_id, season=season, per_mode_simple='Totals', date_to_nullable=g_date, date_from_nullable=g_date)
                time.sleep(1)

                defense_df = defense.get_data_frames()[0]
                defense_df['GAME_ID'] = g_id
                defense_df['PLAYER_ID'] = p_id
                defense_df = defense_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {p_id}, Game {g_id} resulted in an error for defense api")
                defense_df = pd.DataFrame([[p_id, g_id]], columns=['PLAYER_ID', 'GAME_ID'])
                defense_df = defense_df.set_index(['GAME_ID', 'PLAYER_ID'])


            passes_shots = passes_df.join(shots_df, how='left', rsuffix='_shot')
            passes_shots_rebs = passes_shots.join(rebs_df, how='left', rsuffix='_rebs')
            passes_shots_rebs_defense = passes_shots_rebs.join(defense_df, how='left', rsuffix='_defns')
            passes_shots_rebs_defense = passes_shots_rebs_defense.reset_index()

            p_df_dict[g_id] = passes_shots_rebs_defense


        player_df = pd.concat(p_df_dict.values(), ignore_index=True)
        players_dict[p_id] = player_df

    return players_dict

def writeDictToCSV(players_dict):

    players_df = pd.concat(players_dict.values(), ignore_index=True)
    players_df.to_csv('players_df.csv')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument('team', help='The team of interest', type=str)
    parser.add_argument('season', help='The season of interest', type=str)
    
    args = vars(parser.parse_args())

    print("Getting all players in the season chosen...")
    nba_teams, all_players = getAllPlayers(args['season'])
    print("Getting all players for the team chosen...")
    team_players, team_id = getTeamPlayers(nba_teams, all_players, args['team'])
    print("Getting all games for the season chosen...")
    season_games = getSeasonGames(team_id, args['season'])
    print("Creating Tuples of Games and Dates")
    game_dates = createGameDateTuples(season_games)
    print("Getting relevant player data for all games in the season (this takes a long time)...")
    players_dict = collectPlayerData(team_players, game_dates, team_id, args['season'])
    print("Writing player dictionary to file...")
    writeDictToCSV(players_dict)
    print("Writing season games dataframe to file...")
    season_games.to_csv(f'{args['season']}_{args['team']}.csv')