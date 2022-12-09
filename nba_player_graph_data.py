import pandas as pd
import numpy as np
import argparse
import time
from tqdm import tqdm

from nba_api.stats.endpoints import playerdashptpass, commonplayerinfo

def GroupGameDetails(game_details):

    game_details_stats = ['FGM', 'FGA', 'FG3M', 
                          'FG3A', 'FTM', 'FTA', 
                          'OREB', 'DREB', 'REB', 
                          'AST', 'STL', 'BLK', 
                          'TO', 'PF', 'PTS']
    game_details_grouped = games_details.groupby(['TEAM_ID', 'GAME_ID'])[game_details_stats].sum()
    game_details_grouped['FG_PCT'] = game_details_grouped['FGM']/(game_details_grouped['FGM']+game_details_grouped['FGA'])
    game_details_grouped['FG3_PCT'] = game_details_grouped['FG3M']/(game_details_grouped['FG3M']+game_details_grouped['FG3A'])
    game_details_grouped['FT_PCT'] = game_details_grouped['FTM']/(game_details_grouped['FTM']+game_details_grouped['FTA'])
    
    return game_details_grouped

def ReadAndCleanFiles():

    games = pd.read_csv('games.csv')
    players = pd.read_csv('players.csv')
    teams = pd.read_csv('teams.csv')
    ranking = pd.read_csv('ranking.csv')
    games_details = pd.read_csv('games_details.csv')
    all_nba_passes = pd.read_pickle('all_nba_passes.pkl')
    
    games_dtypes = {'GAME_ID': 'int32', 'GAME_STATUS_TEXT': 'str', 'HOME_TEAM_ID': 'int32',
                    'VISITOR_TEAM_ID': 'int32', 'SEASON': 'int32', 'TEAM_ID_home': 'int32', 
                    'TEAM_ID_away': 'int32', 'HOME_TEAM_WINS': 'int32'}
    games_drop_columns = ['PTS_home', 'FG_PCT_home', 'FT_PCT_home', 
                          'FG3_PCT_home', 'AST_home', 'REB_home', 
                          'PTS_away', 'FG_PCT_away', 'FT_PCT_away', 
                          'FG3_PCT_away', 'AST_away', 'REB_away']

    teams_dtypes = {'LEAGUE_ID': 'int32', 'TEAM_ID': 'int32', 'MIN_YEAR': 'int32', 'MAX_YEAR': 'int32', 
                    'ABBREVIATION': 'str', 'NICKNAME': 'str', 'YEARFOUNDED': 'int32', 'CITY': 'str', 
                    'ARENA': 'str', 'ARENACAPACITY': 'float32', 'OWNER': 'str', 'GENERALMANAGER': 'str',
                    'HEADCOACH': 'str', 'DLEAGUEAFFILIATION': 'str'}

    players_dtypes = {'PLAYER_NAME': 'str', 'TEAM_ID': 'int32', 'PLAYER_ID': 'int32', 'SEASON': 'int32'}

    ranking_dtypes = {'TEAM_ID': 'int32', 'LEAGUE_ID': 'int32', 'SEASON_ID': 'int32', 'CONFERENCE': 'str',
                      'TEAM': 'str', 'G': 'int32', 'W': 'int32', 'L': 'int32', 'W_PCT': 'float32', 
                      'HOME_RECORD': 'str', 'ROAD_RECORD': 'str', 'RETURNTOPLAY': 'float32'}

    game_details_grouped = GroupGameDetails(game_details)
    
    games_details_dtypes = {'GAME_ID': 'int32', 'TEAM_ID': 'int32', 'TEAM_ABBREVIATION': 'str', 
                            'TEAM_CITY': 'str', 'PLAYER_ID': 'int32', 'PLAYER_NAME': 'str', 'NICKNAME': 'str',
                            'START_POSITION': 'str', 'COMMENT': 'str', 'MIN': 'str', 
                            'FGM': 'float32', 'FGA': 'float32', 'FG_PCT': 'float32', 'FG3M': 'float32', 
                            'FG3A': 'float32', 'FG3_PCT': 'float32', 'FTM': 'float32', 'FTA': 'float32', 
                            'FT_PCT': 'float32', 'OREB': 'float32', 'DREB': 'float32', 'REB': 'float32', 
                            'AST': 'float32', 'STL': 'float32', 'BLK': 'float32', 'TO': 'float32', 'PF': 'float32',
                            'PTS': 'float32', 'PLUS_MINUS': 'float32'}

    games['GAME_DATE_EST'] = pd.to_datetime(games['GAME_DATE_EST'])
    ranking['STANDINGSDATE'] = pd.to_datetime(ranking['STANDINGSDATE'])

    games = games.drop(columns=games_drop_columns)
    games = games.astype(games_dtypes)
    teams = teams.astype(teams_dtypes)
    players = players.astype(players_dtypes)
    ranking = ranking.astype(ranking_dtypes)
    games_details = games_details.astype(games_details_dtypes)

    return games, teams, players, ranking, games_details, game_details_grouped, all_nba_passes

def CreateTeamStatsDataframe(games, teams, game_details_grouped):

    team_cols = ['ABBREVIATION', 'NICKNAME', 'CITY', 'ARENA', 'ARENACAPACITY']
    home_team_games = games.drop_duplicates().set_index('HOME_TEAM_ID').join(teams.set_index('TEAM_ID')[team_cols], how='left')
    home_team_games = home_team_games.rename(columns={x: f'{x}_home' for x in team_cols})
    home_team_games = home_team_games.reset_index().rename(columns={'index': 'HOME_TEAM_ID'})
    team_games = home_team_games.set_index('VISITOR_TEAM_ID').join(teams.set_index('TEAM_ID')[team_cols], how='left')
    team_games = team_games.rename(columns={x: f'{x}_away' for x in team_cols})
    team_games = team_games.reset_index().rename(columns={'index': 'VISITOR_TEAM_ID'})

    team_games_obj = team_games.select_dtypes(['object'])
    team_games[team_games_obj.columns] = team_games_obj.apply(lambda x: x.str.strip())
    
    home_game_details_grouped = game_details_grouped.reset_index().rename(columns={'TEAM_ID': 'HOME_TEAM_ID'}).set_index(['HOME_TEAM_ID', 'GAME_ID'])
    home_game_details_grouped = home_game_details_grouped.rename(columns={x: f'{x}_home' for x in game_details_grouped.columns})

    away_game_details_grouped = game_details_grouped.reset_index().rename(columns={'TEAM_ID': 'VISITOR_TEAM_ID'}).set_index(['VISITOR_TEAM_ID', 'GAME_ID'])
    away_game_details_grouped = away_game_details_grouped.rename(columns={x: f'{x}_away' for x in game_details_grouped.columns})

    team_games_home_stats = team_games.set_index(['HOME_TEAM_ID', 'GAME_ID']).join(home_game_details_grouped, how='left')
    team_games_stats = team_games_home_stats.reset_index().set_index(['VISITOR_TEAM_ID', 'GAME_ID']).join(away_game_details_grouped, how='left').reset_index()

    return team_games_stats

def FilteringToSeasonPlayoffs(team_games_stats, season, first_playoff_day):

    season_games = team_games_stats[team_games_stats['SEASON']==season]

    season_games.loc[:, 'HOME_TEAM'] = season_games['CITY_home'] + ' ' + season_games['NICKNAME_home']
    season_games.loc[:, 'AWAY_TEAM'] = season_games['CITY_away'] + ' ' + season_games['NICKNAME_away']

    stats_columns = ['FGM_home', 'FGA_home', 'FG3M_home', 'FG3A_home', 'FTM_home',
                     'FTA_home', 'OREB_home', 'DREB_home', 'REB_home', 'AST_home',
                     'STL_home', 'BLK_home', 'TO_home', 'PF_home', 'PTS_home', 'FG_PCT_home',
                     'FG3_PCT_home', 'FT_PCT_home', 'FGM_away', 'FGA_away', 'FG3M_away',
                     'FG3A_away', 'FTM_away', 'FTA_away', 'OREB_away', 'DREB_away',
                     'REB_away', 'AST_away', 'STL_away', 'BLK_away', 'TO_away', 'PF_away',
                     'PTS_away', 'FG_PCT_away', 'FG3_PCT_away', 'FT_PCT_away']

    cols_keep = ['HOME_TEAM', 'HOME_TEAM_ID', 'AWAY_TEAM', 'VISITOR_TEAM_ID', 'GAME_ID', 'GAME_DATE_EST'] + stats_columns + ['HOME_TEAM_WINS']
    season_playoff_games = season_games[season_games['GAME_DATE_EST']>=first_playoff_day][cols_keep]

    return season_playoff_games

def JoinPlayerStats(home_team_games, away_team_games, game_details):

    player_games = home_team_games.set_index(['GAME_ID', 'PLAYER_ID']).add_suffix('_home').join(away_team_games.set_index(['GAME_ID', 'PLAYER_ID']).add_suffix('_away'))
    players_df = player_games.join(games_details.set_index(['GAME_ID', 'PLAYER_ID']), how='left').reset_index()

    return players_df

def CollectPlayerPassingData(players, season, season_playoff_games, game_details):

    home_team_games_dict = {}
    away_team_games_dict = {}
    season_players = players[players['SEASON']==season]

    for game_id in tqdm(season_playoff_games['GAME_ID'].unique()):
        g = season_playoff_games[season_playoff_games['GAME_ID']==game_id][['HOME_TEAM_ID', 'VISITOR_TEAM_ID', 'GAME_DATE_EST']]
        game_date = g['GAME_DATE_EST'].values[0]

        home_players_dict = {}
        home_g_p = season_players[season_players['TEAM_ID']==g['HOME_TEAM_ID'].values[0]] 
        for player_id in home_g_p['PLAYER_ID'].unique():
            try:
                passes = playerdashptpass.PlayerDashPtPass(team_id=str(g['HOME_TEAM_ID'].values[0]), player_id=str(player_id), season=f"{season}-{str(season+1)[-2:]}", season_type_all_star="Playoffs",
                                                           per_mode_simple='Totals', date_to_nullable=str(game_date), date_from_nullable=str(game_date))
                time.sleep(1)

                passes_df = passes.get_data_frames()[0]
                if passes_df.empty:
                    passes_df['PLAYER_ID'] = player_id

                passes_df['GAME_ID'] = game_id
                # passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {player_id}, Game {game_id} resulted in an error for passes api")
                passes_df = pd.DataFrame([[player_id,game_id]], columns=['PLAYER_ID', 'GAME_ID'])
                # passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])

            home_players_dict[player_id] = passes_df

        home_players = pd.concat(home_players_dict.values(), ignore_index=True)
        home_team_games_dict[game_id] = home_players   

        away_players_dict = {}
        away_g_p = season_players[season_players['TEAM_ID']==g['VISITOR_TEAM_ID'].values[0]]
        for player_id in away_g_p['PLAYER_ID'].unique():
            try:
                passes = playerdashptpass.PlayerDashPtPass(team_id=str(g['VISITOR_TEAM_ID'].values[0]), player_id=str(player_id), season=f"{season}-{str(season+1)[-2:]}", season_type_all_star="Playoffs",
                                                           per_mode_simple='Totals', date_to_nullable=str(game_date), date_from_nullable=str(game_date))            
                time.sleep(1)

                passes_df = passes.get_data_frames()[0]
                if passes_df.empty:
                    passes_df['PLAYER_ID'] = player_id

                passes_df['GAME_ID'] = game_id
                # passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])
            except:
                print(f"Player {player_id}, Game {game_id} resulted in an error for passes api")
                passes_df = pd.DataFrame([[player_id,game_id]], columns=['PLAYER_ID', 'GAME_ID'])
                # passes_df = passes_df.set_index(['GAME_ID', 'PLAYER_ID'])

            away_players_dict[player_id] = passes_df

        away_players = pd.concat(away_players_dict.values(), ignore_index=True)
        away_team_games_dict[game_id] = away_players

    home_team_games = pd.concat(home_team_games_dict.values(), ignore_index=True)
    away_team_games = pd.concat(away_team_games_dict.values(), ignore_index=True)
    
    player_df = JoinPlayerStats(home_team_games, away_team_games, game_details)

    return player_df

def GetPlayerPosition(player_id):
    
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    position = player_info.common_player_info.get_data_frame()['POSITION'][0]
    
    time.sleep(1)
    return position

def NormalizePassingFrequency(player_df, all_nba_passes):
    
    player_positions = {}
    for player_id in players_df['PLAYER_ID'].unique():
        player_positions[player_id] = GetPlayerPosition(player_id)

    player_positions_df = pd.DataFrame.from_dict(player_positions, orient='index', columns=['POSITION']).reset_index().rename(columns={'index': 'PLAYER_ID'})
    players_df = players_df.merge(player_positions_df, on=['PLAYER_ID'], how='left')
    players_df = players_df.merge(all_nba_passes, on=['POSITION'], how='left')
    
    players_df['FREQUENCY'] = (players_df['FREQUENCY'] - players_df['mean']) / players_df['std']
    
    return players_df
    
def writeDictToCSV(players_dict):

    players_df = pd.concat(players_dict.values(), ignore_index=True)
    players_df.to_csv('players_df.csv')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument('season', help='The season of interest', type=str)
    parser.add_argument('first_playoff_date', help='The first day of playoff games in this season', type=str)
    
    args = vars(parser.parse_args())

    print("Getting all games, teams, players and more...")
    games, teams, players, ranking, games_details, game_details_grouped, all_nba_passes = ReadAndCleanFiles()
    print("Getting all stats for teams...")
    team_games_stats = CreateTeamStatsDataframe(games, teams, game_details_grouped)
    print("Filtering for the season chosen and only games after first playoff dates...")
    season_playoff_games = FilteringToSeasonPlayoffs(team_games_stats, args['season'], args['first_playoff_date'])
    print("Getting relevant player data for all games in the season (this takes a long time)...")
    players_df = CollectPlayerPassingData(players, args['season'], season_playoff_games, games_details)
    print("Normalizing player passing data by position...")
    normalized_players_df = NormalizePassingFrequency(players_df, all_nba_passes)
    print("Writing player dataframe to file...")
    normalized_players_df.to_csv(f'{args['season']}_Playoffs_Players.csv')
    print("Writing season games dataframe to file...")
    season_playoff_games.to_csv(f'{args['season']}_Playoffs.csv', index=False)
