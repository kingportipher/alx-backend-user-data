from sqlalchemy.orm.session import Session
from user import User


class DB:
    """DB class to manage database operations
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database
        
        Args:
            email (str): The user's email
            hashed_password (str): The user's hashed password
        
        Returns:
            User: The created User object
        """
        new_user = User(email=email, hashed_password=hashed_password)
        session = self._session  # Get the memoized session
        
        session.add(new_user)  # Add the new user to the session
        session.commit()  # Commit the transaction to the database
        session.refresh(new_user)  # Refresh the instance to load new attributes like 'id'
        
        return new_user

