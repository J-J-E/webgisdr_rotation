# Backup Rotation Script

The backup rotation script is designed to manage and rotate ArcGIS WebGIS Disaster Recovery backups based on specified retention parameters. It helps you maintain a manageable number of backups while ensuring that you retain backups according to your desired schedule.

## Features

- Rotates backups based on daily, weekly, monthly, and yearly retention policies.
- Supports dry run mode to simulate backup rotation without actually deleting files. Dry Run Provides detailed output about files to keep and files to delete.


## Requirements

- Python 3.2+

## Installation

1. Clone the repository:

    ```bash
    git clone git@github.com:J-J-E/webgisdr_rotation.git
    ```

## Usage

Run the script with the desired backup folder and retention parameters. Here's the basic usage:

```bash
python rotate_backups.py <backup_folder> [options]
```

#### Optional Arguments:

- `--daily_backups <count>`: Number of daily backups to keep (default: 7).
- `--weekly_backups <count>`: Number of weekly backups to keep (default: 4).
- `--day_of_week <day>`: Day of the week for weekly backup (0 for Monday, 1 for Tuesday, ..., 6 for Sunday) (default: 5).
- `--monthly_backups <count>`: Number of monthly backups to keep (default: 12).
- `--yearly_backups`: Keep yearly backups indefinitely.
- `--dry_run`: Perform a dry run without deleting files.

### Example:

```bash
python rotate_backups.py /path/to/backups --daily_backups 7 --weekly_backups 4 --day_of_week 5 --monthly_backups 12 --yearly_backups --dry_run
```
