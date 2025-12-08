#!/bin/bash
# Setup script for daily cron job to refresh NBA data
# This script adds a cron job to run refresh_data.py daily at 2 AM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
REFRESH_SCRIPT="$SCRIPT_DIR/refresh_data.py"
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Make refresh script executable
chmod +x "$REFRESH_SCRIPT"

# Create cron job entry (runs daily at 5:30 AM)
CRON_TIME="30 5 * * *"
CRON_JOB="$CRON_TIME cd $SCRIPT_DIR && $PYTHON_PATH $REFRESH_SCRIPT >> $LOG_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$REFRESH_SCRIPT"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "$REFRESH_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✓ Cron job successfully added!"
echo ""
echo "Cron job details:"
echo "  Schedule: Daily at 5:30 AM"
echo "  Script: $REFRESH_SCRIPT"
echo "  Logs: $LOG_DIR/cron.log"
echo ""
echo "To view your current cron jobs, run: crontab -l"
echo "To remove this cron job, run: crontab -e (then delete the line)"

