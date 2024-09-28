from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import query
from user import User

class DB:
    """DB class to manage database operations
    """

    def __init__(self) -> None:
        """Initialize a new DB instance"""
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database"""
        new_user = User(email=email, hashed_password=hashed_password)
        session = self._session  # Get the memoized session
        session.add(new_user)
        session.commit()
        session.refresh(new_user)  # Refresh to load new attributes like 'id'
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Find a user by arbitrary keyword argumen
        """
        session = self._session  # Get the memoized session
        try:
            # Perform query based on arbitrary keyword arguments (kwargs)
            user = session.query(User).filter_by(**kwargs).one()
            return user
        except NoResultFound:
            raise NoResultFound("No result found for the query.")
        except InvalidRequestError:
            raise InvalidRequestError("Invalid query arguments.")

