import base64
import gzip
import json
import logging
import os
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
        self.gh_token = os.environ.get("GH_TOKEN", None)
        self.table_name = os.environ.get("TABLE_NAME", "stars")
        self.db_headers = {}
        self.prod = os.environ.get("ENV", False) == "production"
        self.log = self.log_config()
        self.db_config()
        self.base_url = "https://data.gharchive.org"
        self.gh_base_url = "https://api.github.com"
        self.hours = 2
        self.events = []
        self.most_stared = []
        self.schema = {
            "id": 0,
            "actor_id": 1,
            "actor_login": 2,
            "repo_id": 3,
            "repo_name": 4,
            "created_at": 5,
        }

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
        if self.prod == True:
            self.log.info("Connecting to production database (env set to production)")
        else:
            self.log.info("Connecting to development database (env set to development)")

            # suppress requests SSL warnings to localhost
            from urllib3.exceptions import InsecureRequestWarning

            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        self.db_host = os.environ.get("DB_HOST", "localhost")
        username = os.environ.get("BASIC_AUTH_USER", "dev")
        password = os.environ.get("BASIC_AUTH_PASS", "dev")
        auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode(
            "utf-8"
        )
        self.db_headers = {
            "Authorization": f"Basic {auth}",
        }

    def clear_events(self):
        """
        Clears all events from the events list
        """
        self.events = []

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

    def write_to_db(self, query):
        """
        Helper method for writing to the timeseries database
        """

        resp = requests.get(
            f"https://{self.db_host}/exec?query={query}",
            headers=self.db_headers,
            verify=self.prod,  # don't use SSL verification if in development
        )

        if resp.status_code != 200:
            raise Exception(
                f"database HTTP error: {resp.text} | status code: {resp.status_code}"
            )

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
                    # event["actor_id"],
                    # event["actor_login"],
                    # event["repo_id"],
                    event["repo_name"],
                    event["created_at"],
                )
            )

        if len(fmt_events) == 0:
            self.log.info("No new events to write to the database")
            return

        base_query = f"INSERT INTO {self.table_name} VALUES "

        # split fmt_events into chunks of 1000
        chunks = [fmt_events[x : x + 1000] for x in range(0, len(fmt_events), 1000)]

        # loops throuh each chunk and send HTTP requests to write to the database
        for chunk in chunks:
            try:
                query = base_query + ",".join(
                    [f"('{event[0]}', '{event[1]}', '{event[2]}')" for event in chunk]
                )
                self.write_to_db(query)
            except Exception as e:
                self.log.error(f"Error writing to database: {e}")
                failed_events += len(chunk)
                continue

        if skipped_events:
            self.log.info(f"Skipped {skipped_events} events")

        if failed_events:
            self.log.info(f"Failed to commit {failed_events} events")

        # get the number of changes
        self.log.info(
            f"Committed {len(self.events) - skipped_events - failed_events} changes to the database"
        )

    def get_most_stared(self, limit=20, hours=None, enrich=True):
        """
        Query the database for the most stared repositories in a given time period
        :param limit: number of results to return
        :param hours: a time period to limit the results to
        :param enrich: enrich the results with the GitHub API
        :return: list of most stared repositories
        """
        # Query the database to find the most stared repos during the given time period
        if not hours:
            if self.prod == True:
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
            if self.prod == True:
                # planetscale query format
                query = "SELECT repo_name, COUNT(*) AS count FROM stars WHERE created_at between %s and %s GROUP BY repo_name ORDER BY count DESC LIMIT %s"
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

        # update the object with the results
        self.most_stared = self.cursor.fetchall()

        if enrich:
            self.most_stared = self.enrich_most_stared()

        # return the result
        return self.most_stared

    def enrich_most_stared(self):
        """
        Enrich the most stared repositories with additional information from the GitHub API
        :return: list of most stared repositories with additional information
        Note: This function will also update the self.most_stared object with the enriched data
        """
        most_stared_enriched = []

        # loop through all the most stared repos and get the additional information
        for repo in self.most_stared:

            # add github token to request for higher rate limit
            headers = {"Authorization": f"Bearer {self.gh_token}"}
            resp = requests.get(f"{self.gh_base_url}/repos/{repo[0]}", headers=headers)

            if resp.status_code != 200:
                self.log.error(
                    f"Error getting repo enrichment data for {repo[0]} - HTTP: {resp.status_code}"
                )
                continue

            repo_data = resp.json()

            # make an API call to get repo contributors data
            contributors_resp = requests.get(
                repo_data["contributors_url"], headers=headers
            )

            if contributors_resp.status_code != 200:
                self.log.error(
                    f"Error getting contributors enrichment data for {repo[0]} - HTTP: {contributors_resp.status_code}"
                )
                continue
            contributors_data = contributors_resp.json()

            # only grab the first 10 contributors
            contributors = contributors_data[:10]

            most_stared_enriched.append(
                {
                    "repo_name": repo[0],
                    "stars": repo[1],
                    "repo_url": f"https://github.com/{repo[0]}",
                    "description": repo_data["description"],
                    "stargazers_count": repo_data["stargazers_count"],
                    "language": repo_data["language"],
                    "forks_count": repo_data["forks_count"],
                    "updated_at": repo_data["updated_at"],
                    "watchers_count": repo_data["watchers_count"],
                    "open_issues_count": repo_data["open_issues_count"],
                    "topics": repo_data["topics"],
                    "license": repo_data["license"],
                    "contributors": contributors,
                }
            )

        self.most_stared = most_stared_enriched
        return self.most_stared

    def run(self):
        """
        Run the StarEvents class
        This method will collect and store the GitHub star events in the database
        """
        self.get_star_events()
        self.write_star_events()
