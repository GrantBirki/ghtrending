import gzip
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta

import requests
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError


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
        self.storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME", "ghtrending")
        self.azure_access_key = os.environ.get("AZURE_ACCESS_KEY", None)
        self.prod = os.environ.get("ENV", False) == "production"
        self.log = self.log_config()
        self.table = None
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
        Currently using Azure Table Storage
        """
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.azure_access_key};EndpointSuffix=core.windows.net"
        table_service_client = TableServiceClient.from_connection_string(
            conn_str=connection_string
        )
        self.log.debug(f"Created table service client for {self.storage_account_name}")

        # set the table class variable to the Azure table client
        self.table = table_service_client.get_table_client(table_name=self.table_name)

        self.log.info(f"Created client to connect to storage table: {self.table_name}")

    def write(self, entities):
        """
        Write a batch of entities to the Azure Table Storage
        :param entities: entities to write to the Azure Table Storage (list)
        :return: created entity object if successful, None if the entity already exists, False if there is an error
        """
        # loop through all the entitites and add them to a list of 'upsert' operations
        operations = []
        for entity in entities:
            operations.append(("upsert", entity))

        try:
            # execute the batch of operations
            return self.table.submit_transaction(operations)
        except ResourceExistsError:
            self.log.warning(f"Skipping RowKey: {entity['RowKey']} - already exists")
            return None
        except Exception as e:
            self.log.error(f"Error writing entity to Azure Table Storage: {e}")
            return False

    def read(self, query, listify=True):
        """
        Execute a query against the Azure Table Storage
        :param query: query to execute
        :param listify: return a list of entities (True) or a generator (False)
        :return: results from the query (list or generator)
        """
        start = time.time()
        try:
            results = self.table.query_entities(query)

            if listify:
                # convert the generator object to a list
                results = list(results)

            end = time.time()
            self.log.info(f"Read query executed in {round(end - start, 2)} seconds")
            return results
        except Exception as e:
            end = time.time()
            self.log.error(f"Read query failed in {round(end - start, 2)} seconds")
            self.log.error(f"Error executing read query: {e}")

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

        # create the tmp/ directory if it doesn't exist
        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        # save the raw data from the http request to a file
        path = f"tmp/{gharchive_timestamp}.json.gz"
        with open(f"tmp/{gharchive_timestamp}.json.gz", "wb") as f:
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

    def sanitize(self, field_name):
        """
        Helper function to sanitize the repo_name since the DB can be sensitive to special characters
        :param repo_name: repo name to sanitize
        :return: sanitized repo name (False if it can't be sanitized) - or the unsanitized repo name
        """
        if (
            field_name == ""
            or field_name == " "
            or field_name == None
            or field_name == False
        ):
            return False

        return field_name.encode("utf-8").decode("utf-8")

    def write_star_events(self):
        """
        Helper function to use the values in self.events to write to the database
        Loops through all events and commits them to the database
        :return: Boolean - True if successful, False if there is an error
        """
        success = True
        skipped_events = 0

        fmt_events = []
        for event in self.events:

            # sanitize the repo_name
            repo_name = self.sanitize(event["repo_name"])
            if not repo_name:
                skipped_events += 1
                continue

            # sanitize the id (star event_id)
            event_id = self.sanitize(event["id"])
            if not event_id:
                skipped_events += 1
                continue

            # append the formatted event to the list
            fmt_events.append(
                {
                    "PartitionKey": "stars",
                    "RowKey": event_id,
                    "repo_name": repo_name,
                    "created_at": datetime.strptime(
                        event["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "actor_login": event["actor_login"],
                    # event["actor_id"],
                    # event["repo_id"],
                }
            )

        # if there are no new events, exit
        if len(fmt_events) == 0:
            self.log.info("No new events to write to the database")
            return

        # split the fmt_events list into chunks of 100 (max batch size)
        chunks = [fmt_events[x : x + 100] for x in range(0, len(fmt_events), 100)]
        total_chunks = len(chunks)

        self.log.info(
            f"Attempting to write {total_chunks} chunks containing {len(fmt_events)} events to the database"
        )

        counter = 1
        for chunk in chunks:
            start = time.time()
            result = self.write(chunk)
            end = time.time()

            if result:
                self.log.info(
                    f"Chunk {counter}/{total_chunks} written successfully in {round(end - start, 2)} seconds"
                )
            elif result is False:
                # if the chunk failed to write, do additional logging/processing
                self.log.warning(
                    f"Chunk {counter}/{total_chunks} failed to write - retrying..."
                )
                result = self.write(chunk)
                if result is False:
                    self.log.error(
                        f"Chunk {counter}/{total_chunks} failed to write on retry - skipping..."
                    )
                    success = False

            counter += 1

        # log the number of events skipped
        if skipped_events > 0:
            self.log.info(f"Skipped {skipped_events} events")

        # get the number of changes
        self.log.info(
            f"Committed {len(self.events) - skipped_events} changes to the database"
        )

        # return the success status of the entire batch operation
        return success

    def get_stars_in_timeslice(self, hours=None, enrich=True, limit=20):
        """
        Query the database for the most stared repositories in a given time period
        :param hours: a time period to limit the results to
        :param enrich: enrich the results with the GitHub API
        :param limit: number of top repos to return (default: 20)
        :return: list of most stared repositories
        """
        start = time.time()

        # the upper bound is now
        upper_bound = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        # the lower bound is now - the number of hours
        lower_bound = (datetime.utcnow() - timedelta(hours=hours)).isoformat(
            timespec="seconds"
        ) + "Z"

        # query the Azure Table Storage for the events within the time period
        query = f"created_at gt datetime'{lower_bound}' and created_at lt datetime'{upper_bound}'"
        data = self.read(query)

        self.log.info(f"Processing {len(data)} events")

        # loop through every result and count the total number of occurances for each repo_name
        # this is done by creating a dictionary where the key is the repo_name and the value is the number of occurances
        # the dictionary is then sorted by the number of occurances and returned
        results = {}
        for entry in data:
            if entry["repo_name"] in results:
                results[entry["repo_name"]] += 1
            else:
                results[entry["repo_name"]] = 1

        # sort the results by the number of occurances
        results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))

        # create a list of the top N repos using the limit parameter
        top_stared_repos = list(results.items())[:limit]

        # update the object with the results
        self.most_stared = top_stared_repos

        self.log.info(
            f"Processed {len(data)} results in {round(time.time() - start, 3)} seconds"
        )

        # if enrich is True, use the GitHub API to enrich the results
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
        self.log.info("Enriching repository data with the GitHub API")
        start = time.time()
        most_stared_enriched = []

        # add github token to request for higher rate limit
        headers = {"Authorization": f"Bearer {self.gh_token}"}

        # loop through all the most stared repos and get the additional information
        for repo in self.most_stared:
            resp = requests.get(
                f"{self.gh_base_url}/repos/{repo[0]}", headers=headers
            )

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

        self.log.info(
            f"Enriched {len(most_stared_enriched)} repositories in {round(time.time() - start, 3)} seconds"
        )

        self.most_stared = most_stared_enriched
        return self.most_stared

    def run(self):
        """
        Run the StarEvents class
        This method will collect and store the GitHub star events in the database
        :return: True if successful, False if not
        """
        self.get_star_events()
        return self.write_star_events()
