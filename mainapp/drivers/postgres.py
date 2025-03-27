import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()

class PostgresDriver:
    def __init__(
        self,
        dbname=None,
        user=None,
        host=None,
        password=None,
        port=None,
        options=None,
        logger=None,
    ):
        self.logger = logger

        self.db_config = {
            "dbname": dbname or os.getenv("POSTGRES_NAME", "timetable"),
            "user": user or os.getenv("POSTGRES_USER", "postgres"),
            "host": host or os.getenv("POSTGRES_HOST", "localhost"),
            "password": password or os.getenv("POSTGRES_PASSWORD", "password"),
            "port": port or os.getenv("POSTGRES_PORT", "5432"),
            "options": options or "-c search_path=public",
            "sslmode": "disable",
        }

        self.__client = None
        self.__cursor = None
        self._connect()

        if logger:
            self.logger.info(f"Postgres object initialized at {datetime.now()}")

    def _connect(self):
        try:
            self.__client = psycopg2.connect(**self.db_config)
            self.__client.autocommit = True
            self.__cursor = self.__client.cursor()
        except psycopg2.Error as ex:
            if self.logger:
                self.logger.error(f"Failed to connect to database: {ex}")
            raise

    def _get_cursor(self):
        if not self.__client or self.__client.closed:
            if self.logger:
                self.logger.info("Reconnecting to database...")
            self._connect()

        if not self.__cursor or self.__cursor.closed:
            self.__cursor = self.__client.cursor()

        return self.__cursor

    def execute_query(self, query, params=None):
        cursor = self._get_cursor()
        try:
            cursor.execute(query, params)
            if cursor.description:  # SELECT query
                results = cursor.fetchall()
                if self.logger:
                    self.logger.info(f"Query executed successfully: {query}")
                return results
            else:  # Non-SELECT query
                if self.logger:
                    self.logger.info(f"Query executed successfully: {query}")
        except psycopg2.Error as ex:
            if self.logger:
                self.logger.error(f"Query failed: {query} with exception {ex}")
            self.__client.close()
            self.__cursor = None
            raise
