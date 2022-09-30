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

        self.log.info(f"created table service client for {self.storage_account_name}")

        # set the table class variable to the Azure table client
        self.table = table_service_client.get_table_client(table_name=self.table_name)

        self.log.info(f"created client to Azure Table Storage: {self.table_name}")

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

    def read(self, query):
        """
        Execute a query against the Azure Table Storage
        :param query: query to execute
        :return: results from the query
        """
        return self.table.query_entities(query)

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

    def db_query(self, query):
        """
        Helper method for querying the timeseries database (reads, writes, deletes, etc)
        :param query: query to execute
        :return: query results
        """

        resp = requests.get(
            f"https://{self.db_host}/exec?query={query}",
            headers=self.db_headers,
            verify=self.prod,  # don't use SSL verification if in development
        )

        if resp.status_code != 200:
            if resp.status_code == 502:
                self.log.warning(
                    f"The query string may be too long on your request! Try reducing the length of your query string"
                )
            raise Exception(
                f"database HTTP error: {resp.text} | status code: {resp.status_code}"
            )

        return resp

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
        """
        skipped_events = 0
        failed_events = 0

        fmt_events = []
        for event in self.events:

            repo_name = self.sanitize(event["repo_name"])
            if not repo_name:
                skipped_events += 1
                continue

            event_id = self.sanitize(event["id"])
            if not event_id:
                skipped_events += 1
                continue

            fmt_events.append(
                (
                    event_id,
                    # event["actor_id"],
                    # event["actor_login"],
                    # event["repo_id"],
                    repo_name,
                    event["created_at"],
                )
            )

        if len(fmt_events) == 0:
            self.log.info("No new events to write to the database")
            return

        base_query = f"INSERT INTO {self.table_name} VALUES "

        # split fmt_events into chunks of 750
        chunks = [fmt_events[x : x + 750] for x in range(0, len(fmt_events), 750)]

        # loops throuh each chunk and send HTTP requests to write to the database
        total_chunks = len(chunks)
        counter = 1
        for chunk in chunks:

            try:
                query = base_query + ",".join(
                    [f"('{event[0]}','{event[1]}','{event[2]}')" for event in chunk]
                )
                self.db_query(query)

                # sleep to avoid overloading the database
                if self.prod:
                    time.sleep(10)
                else:
                    time.sleep(3)

                self.log.info(f"wrote {counter}/{total_chunks} chunks to the database")
            except Exception as e:
                self.log.error(f"Error writing to database (chunk: {counter}): {e}")
                failed_events += len(chunk)
                continue

            counter += 1

        if skipped_events:
            self.log.info(
                f"Skipped {skipped_events} events (due to empty 'repo_name' or 'id' value from gharchive)"
            )

        if failed_events:
            self.log.info(f"Failed to commit {failed_events} events")

        # get the number of changes
        self.log.info(
            f"Committed {len(self.events) - skipped_events - failed_events} changes to the database"
        )

    def get_stars_in_timeslice(self, limit=20, hours=None, enrich=True, dedupe=False):
        """
        Query the database for the most stared repositories in a given time period
        :param limit: number of results to return
        :param hours: a time period to limit the results to
        :param enrich: enrich the results with the GitHub API
        :param dedupe: remove duplicate results
        :return: list of most stared repositories
        """
        start = time.time()
        # Query the database to find the repos with stars during the given time period
        query = f"SELECT id, repo_name FROM 'stars' WHERE created_at > dateadd('h', -{hours}, now()) GROUP BY repo_name ORDER BY repo_name"

        resp = self.db_query(query)
        data = resp.json()["dataset"]

        with open("data.json", "w") as f:
            f.write(json.dumps(data))

        # dedupe the results by looking for duplicate "id" values where id is a string
        if dedupe:
            seen = set()
            # iterate over all the events and select index [0] (the id) and add it to the set
            data = [x for x in data if not (x[0] in seen or seen.add(x[0]))]
            self.log.info(f"Removed {len(data) - len(seen)} duplicate results")

        self.log.info(f"Found {len(data)} results to process")

        # loop through every result and count the total number of occurances for each repo (index 1 - string)
        # this is done by creating a dictionary where the key is the repo name and the value is the number of occurances
        # the dictionary is then sorted by the number of occurances and returned
        results = {}
        for result in data:
            if result[1] in results:
                results[result[1]] += 1
            else:
                results[result[1]] = 1
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        results = results[:limit]

        # update the object with the results
        self.most_stared = results

        self.log.info(
            f"Processed {len(data)} results in {round(time.time() - start, 3)} seconds"
        )

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

        self.log.info(
            f"Enriched {len(most_stared_enriched)} repositories in {round(time.time() - start, 3)} seconds"
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
