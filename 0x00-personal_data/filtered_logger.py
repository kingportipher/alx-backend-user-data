#!/usr/bin/env python3

import logging
from os import getenv
import re
import mysql.connector
from typing import List
import bcrypt

# PII fields to be redacted
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] user_data INFO %(asctime)s: %(message)s"
    SEPARATOR = ";"

    def __init__(self):
        super(RedactingFormatter, self).__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return self.filter_datum(PII_FIELDS, self.REDACTION, message, self.SEPARATOR)

    @staticmethod
    def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
        """
        Replaces the occurrences of PII fields in the log message with '***'.
        """
        for field in fields:
            message = re.sub(f'{field}=[^;]+', f'{field}={redaction}', message)
        return message


def get_logger() -> logging.Logger:
    """
    Function to create a logger named 'user_data' with certain properties.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # StreamHandler with RedactingFormatter
    stream_handler = logging.StreamHandler()
    formatter = RedactingFormatter()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a connector to the MySQL database using environment variables for credentials.
    """
    username = getenv("PERSONAL_DATA_DB_USERNAME", "root")
    password = getenv("PERSONAL_DATA_DB_PASSWORD", "")
    host = getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = getenv("PERSONAL_DATA_DB_NAME")

    return mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=db_name
    )


def hash_password(password: str) -> bytes:
    """
    Hash a password string using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validate if a provided password matches the hashed password.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)


def main():
    """
    Main function to connect to the database, retrieve user data, and log it with PII redaction.
    """
    logger = get_logger()
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()

    for row in rows:
        name, email, phone, ssn, password, ip, last_login, user_agent = row
        log_msg = (
            f"name={name}; email={email}; phone={phone}; ssn={ssn}; "
            f"password={password}; ip={ip}; last_login={last_login}; user_agent={user_agent};"
        )
        logger.info(log_msg)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()

