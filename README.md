# NBA Graph Machine Learning

This repo is the hub for a passion project of mine where I analyzed NBA Playoff games via flow dynamics through graphs. This was an extension of my independent study during my Masters program and I created a script that can help you get your own data if you desire.

The initial Network Analysis story for this project is live here: [Network Analysis of NBA Playoffs via Flow Dynamics](https://animadurkar.medium.com/network-analysis-of-nba-playoffs-via-flow-dynamics-e5d5de70d4af)

## The Objective

Model NBA games as a graph with players as nodes, the pass frequencies between players as edges and shot frequencies to two non-player nodes (Shot Made and Shot Miss). After doing this for each game, you can calculate specific centrality and flow metrics that can be a strong metric for individual and team performance. We can conduct higher level machine learning objectives such as node prediction, edge classification, and graph embeddings as well.

This script leverages the files in this Kaggle dataset as a start:https://www.kaggle.com/nathanlauga/nba-games

Then the script looks at teams in the playoffs for a chosen season and will get all the passing data of players in that season. This script does not include finals or regular season as finals can be too little of data for just two teams and regular season can be too much data for too many teams. Currently this data is not set up to load into a database, but that can be a sensible evolution if I look to deploy it somewhere.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Clone the Repository

Get a copy of this project by simply running the git clone command.

``` git
git clone https://github.com/AniMadurkar/NBA-Graph-Machine-Learning.git
```

## Getting Your Own Data

Run the python script with your chosen season and the date of the first playoff game like below.

``` python
python nba_player_graph_data.py 2019 2020-08-17
```

Warning: This will take a relatively long time. It's looking at each game and each player for the game because that's how the nba_api requires to get the passing data. Also time.sleeps had to be included to make sure we're not crashing due to overloading the api.

This will output two files after:
1. 2019_Playoffs - relevant data on the teams/games during the 2019-20 playoffs
2. 2019_Playoffs_Players - relevant data on the players during the 2019-20 playoffs
