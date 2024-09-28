from db import DB
from typing import Optional, Union
from user import User
import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _generate_session_id() -> str:
    """Generates a unique session ID."""
    return str(uuid4())


class Authentication:
    """Authentication class for user management."""

    def __init__(self, db: DB):
        """Initializes the Authentication class with a DB instance."""
        self._db = db

    def register_user(self, email: str, password: str) -> Optional[User]:
        """Registers a new user
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User with email {email} already exists")
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))

    def validate_login(self, email: str, password: str) -> bool:
        """Checks if the provided credentials are valid for login.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)

    def create_session(self, email: str) -> Optional[str]:
        """Creates a new session for a user.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_session_id()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> Optional[str]:
        """Retrieves the user's email associated with a session ID.
        """
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user.email
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Ends the active session for a user."""
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user.id, session_id=None)
        except NoResultFound:
            pass  # Ignore if user doesn't exist

    def generate_reset_token(self, email: str) -> Optional[str]:
        """Generates a reset password token for a user.
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = _generate_session_id()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError(f"User with email {email} not found")

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates the password for a user using a valid reset token.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            self._db.update_user(user.id, hashed_password=_hash_password(password), reset_token=None)
        except NoResultFound:
            raise ValueError("Invalid reset token")
