# Daily Data Refresh Setup

This project includes automated daily data refresh via cron job to keep NBA player statistics up to date for the current season (2025-26).

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script to automatically configure the cron job:

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

This will:
- Make the refresh script executable
- Add a daily cron job that runs at 5:30 AM
- Create a logs directory for tracking refresh operations

### Option 2: Manual Setup

1. Make the refresh script executable:
   ```bash
   chmod +x refresh_data.py
   ```

2. Add a cron job manually:
   ```bash
   crontab -e
   ```

3. Add this line (runs daily at 5:30 AM):
   ```
   30 5 * * * cd /path/to/nba-fantasy-trade-analyser && /usr/bin/python3 refresh_data.py >> logs/cron.log 2>&1
   ```
   
   Replace `/path/to/nba-fantasy-trade-analyser` with your actual project path and `/usr/bin/python3` with your Python 3 path (find it with `which python3`).

## How It Works

The `refresh_data.py` script:
- Scrapes current season (2025-26) NBA data and saves to `nba_player_averages_2026.csv`
- **Overwrites** the existing CSV file with the latest data (ensures no duplicate entries)
- Logs all operations to `logs/refresh_YYYYMMDD.log`
- Handles errors gracefully with detailed logging

## Manual Refresh

You can manually refresh the data at any time by running:

```bash
python3 refresh_data.py
```

## Viewing Logs

- Daily refresh logs: `logs/refresh_YYYYMMDD.log`
- Cron execution logs: `logs/cron.log`

## Cron Job Management

- View current cron jobs: `crontab -l`
- Edit cron jobs: `crontab -e`
- Remove all cron jobs: `crontab -r` (use with caution!)

## Changing Schedule

To change when the refresh runs, edit the cron job:

```bash
crontab -e
```

Cron format: `minute hour day month weekday`

Examples:
- `30 5 * * *` - Daily at 5:30 AM (current)
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Weekly on Sunday at midnight
- `30 3 * * 1-5` - Weekdays at 3:30 AM

## Troubleshooting

1. **Check if cron is running**: The cron service should be active. On macOS, check with `sudo launchctl list | grep cron`

2. **Verify Python path**: Make sure the Python path in the cron job is correct:
   ```bash
   which python3
   ```

3. **Check permissions**: Ensure the refresh script is executable:
   ```bash
   chmod +x refresh_data.py
   ```

4. **View recent logs**: Check the log files in the `logs/` directory for any errors

5. **Test manually**: Run `python3 refresh_data.py` manually to verify it works

