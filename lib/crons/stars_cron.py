import sys
from pathlib import Path

path_to_utils = Path(__file__).parent.parent / "stars"
sys.path.insert(0, str(path_to_utils))

from stars import StarEvents

if __name__ == "__main__":
    # Collect the gharchive star events from 2 hours ago
    # NOTE: We get the events from 2 hours ago because the gharchive data for the last hour can be incomplete
    star_events = StarEvents()
    star_events.run()
