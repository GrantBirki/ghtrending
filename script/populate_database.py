import sys
import os
from pathlib import Path

path_to_utils = Path(__file__).parent.parent / "src/stars"
sys.path.insert(0, str(path_to_utils))

from stars import StarEvents

DIR = "script/populate"

star_events = StarEvents()

# loop through all files in the populate dir

for file in os.listdir(DIR):
    # get the file name if it ends in .gz
    if not file.endswith(".gz"):
        continue

    # upload to the database
    star_events.get_star_events(direct_path=f"{DIR}/{file}", keep_file=True)
    star_events.write_star_events()
    star_events.clear_events()
