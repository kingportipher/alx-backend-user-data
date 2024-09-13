#!/usr/bin/env python3

import os
import logging
import mysql.connector
from typing import List
from mysql.connector import connection


class RedactingFormatter(logging.Formatter):
    """
    Redacting Formatter class to sanitize log messages by hiding sensitive fields.
    """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(asctime)s %(name)s %(levelname)s %(message)s"
    SEPARATOR = "; "

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Replace PII fields in the log message with the redacted value.
        """
        message = super(RedactingFormatter, self).format(record)
        for field in self.fields:
            message = message.replace(field, self.REDACTION)
        return message


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def get_logger() -> logging.Logger:
    """
    Creates and configures a logger named 'user_data' that only logs up to INFO level.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Create a StreamHandler with RedactingFormatter
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(fields=PII_FIELDS))

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


def get_db() -> connection.MySQLConnection:
    """
    Returns a connection to the database using environment variables.
    """
    db_username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    db_password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    db_host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    try:
        conn = mysql.connector.connect(
            user=db_username,
            password=db_password,
            host=db_host,
            database=db_name
        )
        return conn
    except mysql.connector.Error as err:
        logger = get_logger()
        logger.error(f"Error: {err}")
        return None


def main():
    """
    Main function to retrieve all users and log them in a filtered format.
    """
    # Get logger
    logger = get_logger()

    # Get database connection
    db_conn = get_db()

    if db_conn:
        try:
            cursor = db_conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users;")
            rows = cursor.fetchall()

            for row in rows:
                log_message = (
                    f'name={row["name"]}; email={row["email"]}; phone={row["phone"]}; '
                    f'ssn={row["ssn"]}; password={row["password"]}; ip={row["ip"]}; '
                    f'last_login={row["last_login"]}; user_agent={row["user_agent"]};'
                )
                logger.info(log_message)
        except mysql.connector.Error as err:
            logger.error(f"Error executing query: {err}")
        finally:
            cursor.close()
            db_conn.close()
    else:
        logger.error("Could not connect to the database.")


# Execute the main function only when the module is executed
if __name__ == "__main__":
    main()

