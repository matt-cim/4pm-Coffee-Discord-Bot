import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connector import Connector

'''
Strictly used for testing purposes.
'''

class TestHelpers():

    @staticmethod
    def delete_all_requests():
        """
        Deletes all records from the 'open_groups' and 'open_voice_channels' table
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            DELETE FROM open_groups;
            """
            cursor.execute(query)

            query = """
            DELETE FROM open_voice_channels;
            """
            cursor.execute(query)

    @staticmethod
    def delete_all_ratings():
        """
        Deletes all records from the 'user_ratings' and 'game_ratings' tables
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            DELETE FROM user_ratings;
            """
            cursor.execute(query)

            query = """
            DELETE FROM game_ratings;
            """
            cursor.execute(query)

    @staticmethod
    def get_all_requests_count():
        """
        Gets the number of total records in the 'open_groups' table
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT COUNT(*) FROM open_groups;
            """
            cursor.execute(query)
            return cursor.fetchone()[0]
        
    @staticmethod
    def get_members_for_group(id: str):
        """
        Gets the array of members who have joined a group
        @param id (str): unique identifier of the record 
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT members
            FROM open_groups
            WHERE id = (%s)
            LIMIT 1;
            """
            cursor.execute(query, (id,))
            return cursor.fetchone()[0]
        
    @staticmethod
    def get_all_voice_channels_count():
        """
        Gets the number of total records in the 'open_voice_channels' table
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT COUNT(*) FROM open_voice_channels;
            """
            cursor.execute(query)
            return cursor.fetchone()[0]

    @staticmethod
    def get_all_ids():
        """
        Gets the list of ids in the 'open_groups' table
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT id FROM open_groups;
            """
            cursor.execute(query)
            return cursor.fetchall()
        
    @staticmethod
    def get_all_open_group_ids():
        """
        Gets the list of 'open_groups_id''s in the 'open_voice_channels' table
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT open_groups_id FROM open_voice_channels;
            """
            cursor.execute(query)
            return cursor.fetchall()
        
    @staticmethod
    def get_record_at_id(id: str):
        """
        Gets record for a certain unique id
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT *
            FROM open_groups
            WHERE id = (%s);
            """
            cursor.execute(query, (id,))
            return cursor.fetchall()
        