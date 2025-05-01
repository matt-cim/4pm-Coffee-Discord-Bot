from database.connector import Connector
from datetime import datetime

'''
Data models for the tables of the database
Gotchas: for string literals in queries need single quotes, double confuse SQL
         always use %s for all types, per psycopg2 docs
         need trailing comma in second parameter of execute()
'''

class OpenRequests():

    @staticmethod
    def insert_request(game: str, username: str, group_size: int, people_needed: int, description: str, channel_id: str, creation_time: datetime):
        """
        Inserts a lfg creation post into db by updating the "open_groups" and "open_voice_channels" tables
        @param game (str): game for the group
        @param username (str): unique id of the user creating the group
        @param group_size (int): # of people requested for group
        @param people_needed (int): group_size - # of people joined
        @param channel_id (str): unique id for the new voice channel
        @param description (str): optional description for group
        @param creation_time (datetime): when the lfg post was created
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            INSERT INTO open_groups (game, username, group_size, people_needed, description, creation_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            cursor.execute(query, (game, username, group_size, people_needed, description, creation_time,))
            open_groups_id = cursor.fetchone()[0]

            query = """
            INSERT INTO open_voice_channels (open_groups_id, channel_id, username, creation_time)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (open_groups_id, channel_id, username, creation_time,))

    @staticmethod
    def get_top_open_requests(game: str):
        """
        Grabs the open requests that are closest to having the 
        preferred amount of people needed for a specific game
        @param game (str): game user wants to join a group for
        @return top 10 open requests as list of tuples or an empty 
                list if there is no records to fetch
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT * FROM open_groups
            WHERE game = (%s)
            ORDER BY people_needed ASC
            LIMIT 10;
            """
            cursor.execute(query, (game,))

            return cursor.fetchall()
        
    @staticmethod
    def get_top_open_requests_all():
        """
        Grabs the open requests that are closest to having the 
        preferred amount of people needed
        @return top 9 open requests as list of tuples or an empty 
                list if there is no records to fetch
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT * FROM open_groups
            ORDER BY people_needed ASC
            LIMIT 9;
            """
            cursor.execute(query, ())

            return cursor.fetchall()
        
    @staticmethod
    def user_joined_group(id: str, username: str) -> bool:
        """
        Decrement the 'people_needed' field for the group
        and delete the group record if everyone has joined
        @param id (str): unique identifier of the record 
        corresponding to the joined group
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            verify_query = """
            SELECT array_position(members, %s) IS NULL
            FROM open_groups
            WHERE id = (%s) AND username != (%s);
            """
            cursor.execute(verify_query, (username, id, username))
            ret = cursor.fetchone()
            allowed_to_join = False if ret is None else ret[0]
            # Users cannot join a group more than once or one they've created
            if allowed_to_join:
                query = """
                UPDATE open_groups
                SET people_needed = people_needed - 1,
                    members = array_append(members, %s)
                WHERE id = (%s);

                DELETE FROM open_groups
                WHERE people_needed < 1
                AND id = (%s);
                """
                cursor.execute(query, (username, id, id,))
                return True
            else:
                return False
            
    @staticmethod
    def delete_open_group(username: str) -> bool:
        """
        Deletes the user's current open group they created
        @param username (str): unique id of the user (creator)
        @return whether they had an open group to delete
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            exists_query = """
            SELECT EXISTS (
                SELECT 1 FROM open_groups WHERE username = %s
            );
            """
            cursor.execute(exists_query, (username,))
            if cursor.fetchone()[0]:
                delete_query = """
                DELETE FROM open_groups 
                WHERE username = %s;
                """
                cursor.execute(delete_query, (username,))
                return True
            else:
                return False

class VoiceChannels():

    @staticmethod
    def get_old_voice_channels():
        """
        Return voice channels that have been open for more than 
        four hours. All times are stored/compared using UTC
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT * FROM open_voice_channels
            WHERE creation_time < (NOW() AT TIME ZONE 'UTC') - INTERVAL '4 hours';
            """
            cursor.execute(query)

            return cursor.fetchall()
        
    @staticmethod
    def get_joined_group_id_for_member_or_creator(username: str):
        """
        @param username (str): unique id of the user (joined member or creator)
        @return possible id for the group the user is in
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT id
            FROM open_groups
            WHERE %s = ANY(members)
            OR username = %s;
            """
            cursor.execute(query, (username, username,))

            return cursor.fetchone()
        
    @staticmethod
    def get_record_by_id(group_id: str):
        """
        @param group_id (str): unique identifier of the record 
        corresponding to the group
        @return voice channel id corresponding to the group
        it was created for
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT * FROM open_voice_channels
            WHERE open_groups_id = %s;
            """
            cursor.execute(query, (group_id,))
            ret = cursor.fetchone()

            return None if ret is None else ret[1]
        
    @staticmethod
    def delete_voice_channels(ids: list[str]):
        """
        Delete voice channels by unique id. Used after finding the channels
        that are no longer in use.
        """
        if not ids:
            return # no voice channels to delete

        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            DELETE FROM open_voice_channels
            WHERE channel_id IN %s;
            """
            cursor.execute(query, (tuple(ids),))

class UserRatings():

    @staticmethod
    def insert_rating(username: str, rating: int):
        """
        Inserts a user rating into db by updating the "user_ratings" table
        @param username (str): unique id of the user being rated
        @param rating (int): [1,5]
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            INSERT INTO user_ratings (username, rating_count, rating_sum, average_rating)
            VALUES (%s, 1, %s, %s)
            ON CONFLICT (username) DO UPDATE
            SET 
                rating_count = user_ratings.rating_count + 1,
                rating_sum = user_ratings.rating_sum + EXCLUDED.rating_sum,
                average_rating = ROUND((user_ratings.rating_sum + EXCLUDED.rating_sum) / (user_ratings.rating_count + 1)::numeric, 2);
            """
            # for first rating, the initial average_rating is the rating itself (otherwise ignored)
            average_rating = rating

            cursor.execute(query, (username, rating, average_rating))

    @staticmethod
    def get_rating(username: str):
        """
        Gets user rating from "user_ratings" table that has already been averaged
        @param username (str): unique id of the user being search for their rating
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT average_rating
            FROM user_ratings
            WHERE username = %s;
            """
            cursor.execute(query, (username,))
            ret = cursor.fetchone()

            return None if ret is None else ret[0]
        
class GameRatings():

    @staticmethod
    def insert_rating(game: str, rating: int):
        """
        Inserts a game rating into db by updating the "game_ratings" table
        @param game (str): game being rated
        @param rating (int): [1,5]
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            INSERT INTO game_ratings (game, rating_count, rating_sum, average_rating)
            VALUES (%s, 1, %s, %s)
            ON CONFLICT (game) DO UPDATE
            SET 
                rating_count = game_ratings.rating_count + 1,
                rating_sum = game_ratings.rating_sum + EXCLUDED.rating_sum,
                average_rating = ROUND((game_ratings.rating_sum + EXCLUDED.rating_sum) / (game_ratings.rating_count + 1)::numeric, 2);
            """
            # for first rating, the initial average_rating is the rating itself (otherwise ignored)
            average_rating = rating

            cursor.execute(query, (game, rating, average_rating))

    @staticmethod
    def get_rating(game: str):
        """
        Gets game rating from "game_ratings" table that has already been averaged
        @param game (str): game being search for rating
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT average_rating
            FROM game_ratings
            WHERE game = %s;
            """
            cursor.execute(query, (game,))
            ret = cursor.fetchone()

            return None if ret is None else ret[0]
        
class Helpers():

    @staticmethod
    def delete_expired_requests():
        """
        Delete group requests that have been open for more than 
        two hours. All times are stored/compared using UTC
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            DELETE FROM open_groups
            WHERE creation_time < (NOW() AT TIME ZONE 'UTC') - INTERVAL '2 hours';
            """
            cursor.execute(query)

    @staticmethod
    def user_has_group_open(username: str) -> bool:
        """
        Used to disallow users to have > 1 outstanding groups open
        @param username (str): unique id of the user requesting to create group
        @return whether they had a group open
        """
        with Connector.DB_POOL.get_cursor() as cursor:
            query = """
            SELECT EXISTS (
                SELECT 1 FROM open_groups WHERE username = %s
            );
            """
            cursor.execute(query, (username,))

            return cursor.fetchone()[0]
