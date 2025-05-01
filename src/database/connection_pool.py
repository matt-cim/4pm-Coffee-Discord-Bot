from contextlib import contextmanager
from psycopg2 import pool
from utils.logger import Logger

'''
Single threaded application, but still using connection pool to limit db connection overhead
'''

DB_NAME = "lfg"

class DatabaseConnectionPool:
    def __init__(self, user, password, host, port):
        self.connection_pool = pool.SimpleConnectionPool(1, # Min. 1 connection
                                                         5, # Could create 5 cursors at once
                                                         user=user,
                                                         password=password,
                                                         host=host,
                                                         port=port,
                                                         database=DB_NAME)

    @contextmanager
    def get_cursor(self):
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        try:
            yield cursor
        except Exception as ex:
            Logger.get_logger().error("Database encountered an error: ", ex, exc_info=True)
            connection.rollback()
        else:
            connection.commit()

        cursor.close()
        self.connection_pool.putconn(connection) # Return to be used again
