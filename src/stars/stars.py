import gzip
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timedelta

import requests


class StarEvents:
    """
    Class for collecting and storing GitHub star events
    """

    def __init__(self):
        """
        Initialize the StarEvents class
        """
        self.log = self.log_config()
        self.conn, self.cursor = self.db_config()
        self.base_url = "https://data.gharchive.org"
        self.hours = 2
        self.events = []

    def log_config(self):
        """
        Create logging configuration
        :return: logger object
        """
        # create a logger for the StarEvents class
        logger = logging.getLogger("StarEvents")
    
        # set the logging level
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(level=log_level)

        # log to stdout
        handler = logging.StreamHandler()

        # set the logging format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # add the handler to the logger
        logger.addHandler(handler)

        # return the logger
        return logger

    def db_config(self):
        """
        Database connections and configuration
        :return: connection and cursor objects
        """

        if os.environ.get("ENV", "development") == "production":
            conn = None  # TODO
            cursor = None  # TODO
        else:
            # connect to the local sqlite database
            conn = sqlite3.connect("data/ghtrending.db")
            cursor = conn.cursor()
            # read sql create table statement
            with open(os.environ.get("STARS_TABLE_SQL", "data/stars.sql"), "r") as f:
                create_star_table = f.read()
            cursor.execute(create_star_table)

        return conn, cursor

    def close(self):
        """
        Close the database connection
        """
        self.conn.close()

    def gharchive_timestamp_fmt(self, timestamp):
        """
        Helper function to format the timestamp for the gharchive url
        :param timestamp: timestamp to format (String or None)
        :return: formatted timestamp in gharchive format
        """

        if timestamp:
            # If the timestamp is provided, use it
            return timestamp
        else:
            # Subtract hour value from the current date and time and use UTC
            timestamp = (datetime.utcnow() - timedelta(hours=self.hours)).strftime("%Y-%m-%d-%H")

        seperated = timestamp.split("-")
        hour = seperated[3]
        # if hour starts with 0, remove the 0
        if hour.startswith("0"):
            hour = hour[1:]
        else:
            hour = hour

        gharchive_timestamp = f"{seperated[0]}-{seperated[1]}-{seperated[2]}-{hour}"

        self.log.info(f"Collecting GitHub star events for {gharchive_timestamp}")

        return gharchive_timestamp

    def gharchive_download(self, timestamp):
        """
        Helper function to download the gharchive file
        :param timestamp: time period to collect events for in gharchive format
        :return: raw data from the http request from the gharchive url
        """
        gharchive_timestamp = self.gharchive_timestamp_fmt(timestamp)

        url = f"https://data.gharchive.org/{gharchive_timestamp}.json.gz"

        self.log.info(f"Downloading events from {url}")

        resp = requests.get(url)

        if resp.status_code != 200:
            self.log.critical(f"Error downloading {url} - HTTP: {resp.status_code}")
            sys.exit(1)

        # save the raw data from the http request to a file
        path = f"data/{gharchive_timestamp}.json.gz"
        with open(f"data/{gharchive_timestamp}.json.gz", "wb") as f:
            f.write(resp.content)

        return path

    def get_star_events(self, timestamp=None):
        """
        Get all GitHub star events for the given time period
        :param timestamp: time period to collect events for in gharchive format
        :return: list of star events
        """

        events = []

        path = self.gharchive_download(timestamp)
        with gzip.open(path, "rb") as f:
            for line in f:

                event = json.loads(line.decode("utf-8"))

                if event["type"] != "WatchEvent" and event["public"] == True:
                    continue

                events.append(
                    {
                        "id": event["id"],
                        "actor_id": event["actor"]["id"],
                        "actor_login": event["actor"]["login"],
                        "repo_id": event["repo"]["id"],
                        "repo_name": event["repo"]["name"],
                        "created_at": event["created_at"],
                    }
                )

        self.log.info(f"Collected {len(events)} GitHub star events")

        # remove the downloaded file
        os.remove(path)

        return events

    def run(self):
        """
        Run the StarEvents class
        This method will collect and store the GitHub star events in the database
        """

        self.events = self.get_star_events()

        skipped_events = 0

        # write all events to the stars table in the ghtrending database, continue if the event already exists in the database table
        for event in self.events:
            try:
                self.cursor.execute(
                    "INSERT INTO stars VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        event["id"],
                        event["actor_id"],
                        event["actor_login"],
                        event["repo_id"],
                        event["repo_name"],
                        event["created_at"],
                    ),
                )
            except sqlite3.IntegrityError:
                self.log.debug(f"Event {event['id']} already exists in the database")
                skipped_events += 1
                continue

        if skipped_events:
            self.log.info(f"Skipped {skipped_events} duplicate events (already in the DB)")

        # self.cursor.executemany(
        #     "INSERT INTO stars VALUES (:id, :actor_id, :actor_login, :repo_id, :repo_name, :created_at)",
        #     self.events,
        # )

        # commit the changes
        self.conn.commit()

        # get the number of changes
        self.log.info(f"Committed {self.conn.total_changes} changes to the database")

        self.close()

    def get_most_stared(self, limit=20, timestamp=None):
        """
        Query the database for the most stared repositories in a given time period
        :param limit: number of results to return
        :param timestamp: a time period to limit the results to
        :return: list of most stared repositories
        """

        # Query the database to find the most stared repos during the given time period
        if not timestamp:
            # if there is no timestamp, get the most stared repos for all time
            self.cursor.execute(
                f"SELECT repo_name, COUNT(*) AS count FROM stars GROUP BY repo_name ORDER BY count DESC LIMIT ?",
                (limit,),
            )

        # return the result
        return self.cursor.fetchall()

if __name__ == "__main__":
    # Collect Star Events
    stars = StarEvents()
    stars.run()

    # Get Star Event Analytics
    stars = StarEvents()
    result = stars.get_most_stared()
    print(result)
