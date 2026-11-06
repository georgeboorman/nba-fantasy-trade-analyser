#!/usr/bin/env python3
"""
Data refresh script for NBA Fantasy Trade Analyser.
This script fetches per-game stats for the tracked NBA seasons and updates
their CSV files. Run this script daily via cron job to keep data up to date.
"""

import sys
import os
from datetime import datetime
import logging

from nba_api.stats.endpoints import leaguedashplayerstats

# Seasons tracked by this app, keyed by the file-name year used throughout
# the rest of the app (matches the convention of the original
# basketball-reference scrape, where e.g. the 2025-26 season is "2026").
SEASONS = {
    2026: "2025-26",
    2027: "2026-27",
}

# Maps nba_api's LeagueDashPlayerStats columns onto the column names the
# rest of this app expects (originally scraped from basketball-reference).
COLUMN_MAP = {
    "PLAYER_NAME": "Player",
    "TEAM_ABBREVIATION": "Team",
    "AGE": "Age",
    "GP": "G",
    "MIN": "MP",
    "FGM": "FG",
    "FGA": "FGA",
    "FG_PCT": "FG%",
    "FG3M": "3P",
    "FG3A": "3PA",
    "FG3_PCT": "3P%",
    "FTM": "FT",
    "FTA": "FTA",
    "FT_PCT": "FT%",
    "OREB": "ORB",
    "DREB": "DRB",
    "REB": "TRB",
    "AST": "AST",
    "TOV": "TOV",
    "STL": "STL",
    "BLK": "BLK",
    "PF": "PF",
    "PTS": "PTS",
}

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'refresh_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def scrape_season_data(year, season):
    """Fetch NBA per game statistics for a given season from stats.nba.com and save to CSV."""
    try:
        logger.info(f"Starting {season} season data scrape...")

        logger.info(f"Fetching data from stats.nba.com for season {season}...")
        response = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            per_mode_detailed="PerGame",
            timeout=30,
        )
        data = response.get_data_frames()[0]

        # Keep and rename only the columns the rest of the app expects
        data = data[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)

        # Adding a column for season
        data['Season'] = round(year)

        # Get absolute path to ensure we save in the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, f'nba_player_averages_{year}.csv')

        # Save to csv (overwrites existing file)
        data.to_csv(csv_path, index=False)
        logger.info(f"Successfully scraped and saved {season} season data to {csv_path} ({len(data)} rows)")
        return True

    except Exception as e:
        logger.error(f"Error in scrape_season_data for {season}: {str(e)}", exc_info=True)
        return False

def main():
    """Main function to run the scraping operation for all tracked seasons."""
    logger.info("=" * 60)
    logger.info("Starting NBA data refresh process")
    logger.info("=" * 60)

    # Change to script directory to ensure relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Run scraping operation for each tracked season
    results = {
        season: scrape_season_data(year, season)
        for year, season in SEASONS.items()
    }

    # Summary
    logger.info("=" * 60)
    logger.info("Data refresh summary:")
    for season, success in results.items():
        logger.info(f"  {season} season data: {'SUCCESS' if success else 'FAILED'}")
    logger.info("=" * 60)

    if all(results.values()):
        logger.info("Data refresh completed successfully!")
        return 0
    else:
        logger.error("Data refresh completed with errors. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
