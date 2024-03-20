import os
import argparse
from datetime import datetime
import re
import calendar

def parse_arguments():
    parser = argparse.ArgumentParser(description="Rotate backups based on retention parameters")
    parser.add_argument("backup_folder", help="Target folder for backup rotation")
    parser.add_argument("--daily_backups", type=int, default=7, help="Number of daily backups to keep (default: 7)")
    parser.add_argument("--weekly_backups", type=int, default=4, help="Number of weekly backups to keep (default: 4)")
    parser.add_argument("--day_of_week", type=int, default=5, choices=range(7), help="Day of the week for weekly backup (0 for Monday, 1 for Tuesday, ..., 6 for Sunday) (default: 5)")
    parser.add_argument("--monthly_backups", type=int, default=12, help="Number of monthly backups to keep (default: 12)")
    parser.add_argument("--yearly_backups", action="store_true", help="Keep yearly backups indefinitely")
    parser.add_argument("--dry_run", action="store_true", help="Perform a dry run without deleting files")
    return parser.parse_args()

def get_backup_date(filename):
    match = re.search(r'(\d{8})-\d{6}-UTC-BACKUP\.\w+', filename)
    if match:
        return datetime.strptime(match.group(1), "%Y%m%d").date()  # Extracting date component
    else:
        return None

def rotate_backups(backup_folder, daily_backups_to_keep, weekly_backups_to_keep, day_of_week_for_weekly_backup, monthly_backups_to_keep, yearly_backups_to_keep, dry_run):
    files = os.listdir(backup_folder)
    backups = [file for file in files if re.match(r'\d{8}-\d{6}-UTC-BACKUP\.\w+', file)]

    backups.sort()
    daily_backups = []
    weekly_backups = []
    monthly_backups = []
    yearly_backups = []

    today = datetime.now().date()

    for backup in backups:
        backup_date = get_backup_date(backup)
        if (today - backup_date).days < daily_backups_to_keep:
            daily_backups.append(backup)
        elif backup_date.weekday() == day_of_week_for_weekly_backup and (today - backup_date).days < 7 * weekly_backups_to_keep:
            weekly_backups.append(backup)
        elif backup_date.day == calendar.monthrange(backup_date.year, backup_date.month)[1]:
             monthly_backups.append(backup)
        elif yearly_backups_to_keep and backup_date.month == 12 and backup_date.day == 31 and backup_date.year < today.year:
            yearly_backups.append(backup)

    if dry_run:
        with open("dry_run_output.txt", "w") as f:
            f.write("Daily Backups:\n")
            daily_backups, daily_size = write_backup_list(f, daily_backups, backup_folder)
            f.write("\nWeekly Backups:\n")
            weekly_backups, weekly_size = write_backup_list(f, weekly_backups, backup_folder)
            f.write("\nMonthly Backups:\n")
            monthly_backups, monthly_size = write_backup_list(f, monthly_backups, backup_folder)
            f.write("\nYearly Backups:\n")
            yearly_backups, yearly_size = write_backup_list(f, yearly_backups, backup_folder)

            # Files to delete section
            f.write("\nFiles to Delete (Ordered by Date Descending):\n")
            deleted_files, deleted_size = write_backup_list(f, sorted(set(backups) - set(daily_backups) - set(weekly_backups) - set(monthly_backups) - set(yearly_backups), key=get_backup_date, reverse=True), backup_folder)
            f.write("\n--------------------------------\n\n")
            f.write("Total size for Daily Backups: {}\n".format(sizeof_fmt(daily_size)))
            f.write("Total size for Weekly Backups: {}\n".format(sizeof_fmt(weekly_size)))
            f.write("Total size for Monthly Backups: {}\n".format(sizeof_fmt(monthly_size)))
            f.write("Total size for Yearly Backups: {}\n".format(sizeof_fmt(yearly_size)))
            total_remaining_size = sum(os.path.getsize(os.path.join(backup_folder, file)) for file in daily_backups + weekly_backups + monthly_backups + yearly_backups)
            f.write("Total size for remaining files: {}\n".format(sizeof_fmt(total_remaining_size)))
            f.write("Total size for file marked for removal: {}\n".format(sizeof_fmt(deleted_size)))

    else:
        backups_to_keep = daily_backups + weekly_backups + monthly_backups + yearly_backups
        deleted_files = sorted(set(backups) - set(backups_to_keep), key=get_backup_date, reverse=True)
        for file in deleted_files:
            os.remove(os.path.join(backup_folder, file))

def write_backup_list(f, backups, backup_folder):
    total_size = 0
    for backup in backups:
        backup_path = os.path.join(backup_folder, backup)
        backup_size = os.path.getsize(backup_path)
        total_size += backup_size
        f.write("{}\n".format(backup))
    f.write("TOTAL SIZE: {}\n".format(sizeof_fmt(total_size)))
    return backups, total_size

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def main():
    args = parse_arguments()
    rotate_backups(args.backup_folder, args.daily_backups, args.weekly_backups, args.day_of_week, args.monthly_backups, args.yearly_backups, args.dry_run)

if __name__ == "__main__":
    main()
