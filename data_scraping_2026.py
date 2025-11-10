import pandas as pd
import numpy as np
import time

# Scrape 2026 NBA per game statistics
year = 2026
url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
data = pd.read_html(url)

# Removing first element from list
data = data.pop(0)

# Adding a column for season
data['Season'] = round(year)

# Drop the Rk column if it exists
if "Rk" in data.columns:
    data.drop(columns=["Rk"], inplace=True)

# Save to csv
data.to_csv('nba_player_averages_2026.csv', index=False)

print(f"Successfully scraped and saved 2026 NBA player averages to nba_player_averages_2026.csv")

