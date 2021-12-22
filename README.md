# NBA Graph Machine Learning

This repo is the hub for a passion project of mine where I analyzed NBA Playoff games via flow dynamics through graphs. This was an extension of my independent study during my Masters program and I created a script that can help you get your own data if you desire.

## The Objective

Model NBA games as a graph with players as nodes, the pass frequencies between players as edges and shot frequencies to two non-player nodes (Shot Made and Shot Miss). After doing this for each game, you can calculate specific centrality and flow metrics that can be a strong metric for individual and team performance.

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

Run the python script with your chosen season to get playoff data for it.

``` python
python .py
```
