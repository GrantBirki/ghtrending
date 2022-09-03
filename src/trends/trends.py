import sys
from pathlib import Path

path_to_utils = Path(__file__).parent.parent / "stars"
sys.path.insert(0, str(path_to_utils))

from stars import StarEvents

# Get Star Event Analytics
star_events = StarEvents()

# Get the most stared repos from all time from the DB
all_time = star_events.get_most_stared()
print(f"All time:\n\n{all_time}\n")

# Get the most stared repos from the past 24 hours
last_24_hours = star_events.get_most_stared(hours=24)
print(f"Last 24 hours:\n\n{last_24_hours}\n")

# Get the most stared repos from the past 7 days
last_7_days = star_events.get_most_stared(hours=24 * 7)
print(f"Last 7 days:\n\n{last_7_days}\n")

# Get the most stared repos from the past 30 days
last_30_days = star_events.get_most_stared(hours=24 * 30)
print(f"Last 30 days:\n\n{last_30_days}\n")

star_events.close()
