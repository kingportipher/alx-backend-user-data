#!/usr/bin/env python3
""" Authentication class.
"""

from db import Database
from typing import TypeVar
from user import User
import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def generate_uuid() -> str:
    """
    Generate a unique UUID string.
    """
    return str(uuid4())


class Authentication:
    """
    Authentication class to manage user-related actions such as registration,
    login, session creation, and password reset.
    """

    def __init__(self):
        """
        Initialize a new Authentication instance with a database connection.
        """
        self.db = Database()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user if the email is not already registered.
        """
        try:
            self.db.find_user_by(email=email)
            raise ValueError(f"User with email {email} already exists.")
        except NoResultFound:
            hashed_pwd = hash_password(password)
            return self.db.add_user(email, hashed_pwd)

    def validate_login(self, email: str, password: str) -> bool:
        """
        Validate the login credentials for a user.
        """
        try:
            user = self.db.find_user_by(email=email)
        except NoResultFound:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))

    def create_session(self, email: str) -> str:
        """
        Create a new session for the user with the given email.
        """
        try:
            user = self.db.find_user_by(email=email)
            session_id = generate_uuid()
            self.db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session(self, session_id: str) -> str:
        """
        Retrieve a user's email based on the session ID.
        """
        if session_id is None:
            return None
        try:
            user = self.db.find_user_by(session_id=session_id)
            return user.email
        except NoResultFound:
            return None

    def end_session(self, user_id: int) -> None:
        """
        Destroy a user's session by setting their session ID to None.
        """
        try:
            user = self.db.find_user_by(id=user_id)
            self.db.update_user(user.id, session_id=None)
        except NoResultFound:
            pass

    def get_reset_token(self, email: str) -> str:
        """
        Generate a password reset token for a user based on their email.
        """
        try:
            user = self.db.find_user_by(email=email)
            reset_token = generate_uuid()
            self.db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError("User not found.")

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update a user's password using a reset token and a new password.
        """
        try:
            user = self.db.find_user_by(reset_token=reset_token)
            new_hashed_password = hash_password(password)
            self.db.update_user(user.id, hashed_password=new_hashed_password, reset_token=None)
        except NoResultFound:
            raise ValueError("Invalid reset token.")

