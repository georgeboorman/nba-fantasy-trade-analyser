import pandas as pd
import numpy as np
import time

seasons_dict = {}
years = range(2015, 2026, 1)

for year in years: 
  # Loop through URLs and scrape data
  url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
  data = pd.read_html(url)

  # Removing first element from list
  data = data.pop(0)
  
  # Adding a column for season
  data['Season'] = round(year)

  # Appending to a single dictionary
  seasons_dict[year] = data

  # Wait to run next query
  time.sleep(1)

# Combine data for all seasons and clean
df = pd.concat(seasons_dict.values())
df.drop(columns=["Rk"], inplace=True)

# Save to csv
df.to_csv('nba_player_averages_per_season.csv', index=False)