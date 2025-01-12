from logging import critical
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from config.config import Config


class Application:
    """This class is the core of the application, meaning that this class manage the base of the application. In other
    words, this class that manage the database, the application environment and loads the configurations.

    The application is created in the init of the bot so it accessible across all the app easily.
    ```
        app = Application()
    `̀̀``

    By default the configuration environment is loaded with `production` but it can be change by exporting the `BOT_ENV`
    environment variable (available environments: `production`, `development`, `test`) or by setting the config with
    the wanted environment.

    Note: The database uses SQLAlchemy ORM (https://www.sqlalchemy.org/).
    """

    # The current opened session.
    # To access the session you should use the session property (Ex. `app.session`)
    __session = None

    def __init__(self):
        self.config = Config()
        self.token = self.config.get("DISCORD_TOKEN")

        self.engine = None
        self.base = declarative_base()

        self.load_database()

    @property
    def session(self):
        """Instantiate the session for querying the database."""
        if Application.__session is None:
            session = sessionmaker(bind=self.engine)
            Application.__session = session()

        return Application.__session

    def load_database(self):
        """Loads and connects to the database using the loaded config"""

        self.engine = create_engine(self.config.database_uri, echo=self.config.environment.SQLALCHEMY_ECHO)

        try:
            self.engine.connect()
        except OperationalError as e:
            critical(f"Unable to create the 'Application': {e}")
            exit()

    def unload_database(self):
        """Unloads the current database"""

        self.engine = None
        Application.__session = None

    def reload_database(self):
        """Reload the database. This function can be use in case there's a dynamic environment change."""

        self.unload_database()
        self.load_database()

    def create_database(self):
        """Creates the current loaded database"""

        if not database_exists(self.config.database_uri):
            create_database(self.config.database_uri)

    def drop_database(self):
        """Drops the current loaded database"""

        if not database_exists(self.config.database_uri):
            drop_database(self.config.database_uri)

    def create_tables(self):
        """Creates all the tables for the current loaded database"""

        self.base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drops all the tables for the current loaded database"""

        self.base.metadata.drop_all(self.engine)
