from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from packages.config import settings

DATABASE_URI = (
    f"postgresql://{settings.db_username}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

# create the postgres database engine
engine = create_engine(DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_add(session: Session, model, commit: bool = True, **kwargs):
    """
    Query whether an entry exists in a table based on key word parameters and add if not found.
    Note kwargs are used to query and add the entry, so they must cover all required parameters.

    Parameters
    ----------
    session: Database session
    model: Table to query
    commit: Whether to commit changes (default True, useful to set False if wrapping in large loop > commit at end)
    kwargs: Parameters to query

    Returns
    -------
    instance: either matching or newly added entry
    """

    # Remove null id if provided, as this will always result in input entry being added
    if kwargs.get("id", False) is None:
        kwargs.pop("id")

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        if commit:
            session.commit()

        return instance
