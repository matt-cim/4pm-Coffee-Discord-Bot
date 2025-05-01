import os
from database.connection_pool import DatabaseConnectionPool
from dotenv import load_dotenv

"""
Only want to create connection pool once during bot's lifespan
"""

class Connector:
    load_dotenv()
    DB_POOL = DatabaseConnectionPool(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), 
                                     host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"))