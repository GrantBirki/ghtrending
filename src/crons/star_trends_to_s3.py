import os
import sys
from pathlib import Path
import json

import boto3

path_to_utils = Path(__file__).parent.parent / "stars"
sys.path.insert(0, str(path_to_utils))

from stars import StarEvents

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
BUCKET_NAME = os.environ.get("BUCKET_NAME", "data.ghtrending.io")
STAR_TRENDS_PATH = os.environ.get("STAR_TRENDS_PATH", "trends/stars")

def upload_to_s3(result):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{STAR_TRENDS_PATH}/{result['name']}.json",
        Body=json.dumps(result["data"]),
        ContentType="application/json",
    )

def main():
    if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
        print("AWS credentials not set. Exiting.")
        sys.exit(1)

    # Get Star Event Trends
    star_events = StarEvents()

    results = []

    # Get the most stared repos from all time from the DB
    results.append({"name": "all_time", "data": star_events.get_most_stared()})

    # Get the most stared repos from the past 24 hours
    results.append({"name": "last_24_hours", "data": star_events.get_most_stared(hours=24)})

    # Get the most stared repos from the past 7 days
    results.append({"name": "last_7_days", "data": star_events.get_most_stared(hours=24 * 7)})

    # Get the most stared repos from the past 30 days
    results.append({"name": "last_30_days", "data": star_events.get_most_stared(hours=24 * 30)})

    star_events.close()

    for result in results:
        upload_to_s3(result)

if __name__ == "__main__":
    main()
