# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import ENVIRONMENT, loaded_config
from models.entities.base import Base

config = loaded_config

DATABASE_URL = config.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    try:
        if ENVIRONMENT.lower() == "production":
            print("Warning: Database initialization should be handled by migrations in production!")
            return

        Base.metadata.create_all(bind=engine)
        print("Database initialized!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database session error: {str(e)}")
        db.rollback()
        db.close()
        return None
    finally:
        db.close()


def reset_database():
    try:
        if ENVIRONMENT.lower() == "production":
            raise EnvironmentError("ERROR: Cannot reset database in production environment!")

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Database reset!")
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return


def create_tables_in_production():
    try:
        if ENVIRONMENT.lower() != "production":
            raise EnvironmentError("ERROR: This method should only be called in a production environment!")

        Base.metadata.create_all(bind=engine)
        print("Production tables created!")
    except Exception as e:
        print(f"Error creating production tables: {str(e)}")
        return
