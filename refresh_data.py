#!/usr/bin/env python3
"""
Data refresh script for NBA Fantasy Trade Analyser.
This script scrapes and updates the current season (2025-26) data CSV file.
Run this script daily via cron job to keep data up to date.
"""

import pandas as pd
import numpy as np
import time
import sys
import os
from datetime import datetime
import logging

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

def scrape_current_season_data():
    """Scrape 2025-26 NBA per game statistics and save to CSV."""
    try:
        logger.info("Starting 2025-26 season data scrape...")
        year = 2026  # 2025-26 season is represented as 2026 in basketball-reference
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
        
        logger.info(f"Fetching data from {url}...")
        data = pd.read_html(url)
        
        # Removing first element from list
        data = data.pop(0)
        
        # Adding a column for season
        data['Season'] = round(year)
        
        # Drop the Rk column if it exists
        if "Rk" in data.columns:
            data.drop(columns=["Rk"], inplace=True)
        
        # Get absolute path to ensure we save in the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, 'nba_player_averages_2026.csv')
        
        # Save to csv (overwrites existing file)
        data.to_csv(csv_path, index=False)
        logger.info(f"Successfully scraped and saved 2025-26 season data to {csv_path} ({len(data)} rows)")
        return True
        
    except Exception as e:
        logger.error(f"Error in scrape_current_season_data: {str(e)}", exc_info=True)
        return False

def main():
    """Main function to run the scraping operation."""
    logger.info("=" * 60)
    logger.info("Starting NBA data refresh process (2025-26 season)")
    logger.info("=" * 60)
    
    # Change to script directory to ensure relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run scraping operation
    success = scrape_current_season_data()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Data refresh summary:")
    logger.info(f"  2025-26 season data: {'SUCCESS' if success else 'FAILED'}")
    logger.info("=" * 60)
    
    if success:
        logger.info("Data refresh completed successfully!")
        return 0
    else:
        logger.error("Data refresh completed with errors. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

