import gzip
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timedelta

import MySQLdb
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
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
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
            conn = MySQLdb.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                user=os.environ.get("DB_USERNAME"),
                passwd=os.environ.get("DB_PASSWORD"),
                db=os.environ.get("DATABASE_NAME"),
                ssl_mode="VERIFY_IDENTITY",
                ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"},
            )
            cursor = conn.cursor()
        else:
            # connect to the local sqlite database
            conn = sqlite3.connect("data/ghtrending.db")
            cursor = conn.cursor()
            # read sql create table statement
            with open(os.environ.get("STARS_TABLE_SQL", "data/stars.sql"), "r") as f:
                create_star_table = f.read()
            cursor.execute(create_star_table)

        return conn, cursor

    def clear_events(self):
        """
        Clears all events from the events list
        """
        self.events = []

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
            timestamp = (datetime.utcnow() - timedelta(hours=self.hours)).strftime(
                "%Y-%m-%d-%H"
            )

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

    def get_star_events(self, timestamp=None, direct_path=None, keep_file=False):
        """
        Get all GitHub star events for the given time period
        :param timestamp: time period to collect events for in gharchive format
        :param direct_path: path to the gharchive file
        :param keep_file: keep the downloaded file
        """
        events = []

        if direct_path:
            path = direct_path
        else:
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
        if keep_file == False:
            os.remove(path)

        self.events = events

    def write_star_events(self):
        """
        Helper function to use the values in self.events to write to the database
        Loops through all events and commits them to the database
        """
        skipped_events = 0
        failed_events = 0

        fmt_events = []
        for event in self.events:
            fmt_events.append(
                (
                    event["id"],
                    event["actor_id"],
                    event["actor_login"],
                    event["repo_id"],
                    event["repo_name"],
                    event["created_at"],
                )
            )

        if os.environ.get("ENV", "development") == "production":
            # planetscale query format
            query = "INSERT INTO stars VALUES (%s, %s, %s, %s, %s, %s)"
        else:
            # sqlite query format
            query = "INSERT INTO stars VALUES (?, ?, ?, ?, ?, ?)"

        try:
            self.cursor.executemany(
                query,
                fmt_events,
            )
            self.conn.commit()
        except (MySQLdb.IntegrityError, sqlite3.IntegrityError):
            self.log.warn(
                "Bulk insert failed (likely due to a duplicate), trying one by one inserts instead"
            )

            # loop through all events and commit them to the database
            for event in self.events:
                try:
                    self.cursor.execute(
                        query,
                        (
                            event["id"],
                            event["actor_id"],
                            event["actor_login"],
                            event["repo_id"],
                            event["repo_name"],
                            event["created_at"],
                        ),
                    )
                except (MySQLdb.IntegrityError, sqlite3.IntegrityError):
                    self.log.debug(
                        f"Event {event['id']} already exists in the database"
                    )
                    skipped_events += 1
                    continue

                except Exception as e:
                    self.log.error(f"Error inserting event {event['id']} - {e}")
                    failed_events += 1
                    continue

        if skipped_events:
            self.log.info(
                f"Skipped {skipped_events} duplicate events (already in the DB)"
            )

        if failed_events:
            self.log.info(f"Failed to commit {failed_events} events")

        self.conn.commit()

        # get the number of changes
        self.log.info(
            f"Committed {len(self.events) - skipped_events} changes to the database"
        )

    def run(self):
        """
        Run the StarEvents class
        This method will collect and store the GitHub star events in the database
        """
        self.get_star_events()
        self.write_star_events()
        self.close()

    def get_most_stared(self, limit=20, hours=None):
        """
        Query the database for the most stared repositories in a given time period
        :param limit: number of results to return
        :param hours: a time period to limit the results to
        :return: list of most stared repositories
        """
        # Query the database to find the most stared repos during the given time period
        if not hours:
            if os.environ.get("ENV", "development") == "production":
                # planetscale query format
                query = "SELECT repo_name, COUNT(*) AS count FROM stars GROUP BY repo_name ORDER BY count DESC LIMIT %s"
            else:
                # sqlite query format
                query = "SELECT repo_name, COUNT(*) AS count FROM stars GROUP BY repo_name ORDER BY count DESC LIMIT ?"

            # if there is no hours value, get the most stared repos for all time
            self.cursor.execute(
                query,
                (limit,),
            )
        else:
            # if there is a hours value, get the most stared repos for the given time period
            if os.environ.get("ENV", "development") == "production":
                # planetscale query format
                query = "SELECT repo_name, COUNT(*) AS count FROM stars WHERE(strftime('%Y-%m%dT%H:%M:%S', created_at) between strftime('%Y-%m%dT%H:%M:%S', %s) and strftime('%Y-%m%dT%H:%M:%S', %s)) GROUP BY repo_name ORDER BY count DESC LIMIT %s"
            else:
                # sqlite query format
                query = "SELECT repo_name, COUNT(*) AS count FROM stars WHERE(strftime('%Y-%m%dT%H:%M:%S', created_at) between strftime('%Y-%m%dT%H:%M:%S', ?) and strftime('%Y-%m%dT%H:%M:%S', ?)) GROUP BY repo_name ORDER BY count DESC LIMIT ?"

            end = datetime.utcnow()
            start = end - timedelta(hours=hours)
            self.cursor.execute(
                query,
                (
                    start.strftime("%Y-%m-%dT%H:%M:%S"),
                    end.strftime("%Y-%m-%dT%H:%M:%S"),
                    limit,
                ),
            )

        # return the result
        return self.cursor.fetchall()
