import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from helpers_tests import TestHelpers
# path only updated for the current runtime this is executed in
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import OpenRequests, Helpers


class TestPostCleaner(unittest.TestCase):
    game = "game"
    username = "username"
    people_needed = group_size = 42
    description = "description"
    channel_id = "1234567891234567890"

    def setUp(self):
        # refresh table before each test
        TestHelpers.delete_all_requests()

    def test_no_delete(self):
        self.assertEqual(0, TestHelpers.get_all_requests_count())

        # brand new lfg request
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, datetime.now(timezone.utc))
        Helpers.delete_expired_requests()
        self.assertEqual(1, TestHelpers.get_all_requests_count())

        # existing requests all made within the last two hours
        creation_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=0, seconds=0)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=59, seconds=0)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=59, seconds=35)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=0, minutes=42, seconds=1)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=0, minutes=1, seconds=60)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=0, minutes=21, seconds=12)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=10, seconds=33)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        Helpers.delete_expired_requests()
        self.assertEqual(8, TestHelpers.get_all_requests_count())

    def test_delete(self):
        self.assertEqual(0, TestHelpers.get_all_requests_count())

        # existing requests that should be deleted because they are > 2 hours old
        creation_time = datetime.now(timezone.utc) - timedelta(hours=2, minutes=0, seconds=0)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=59, seconds=60)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=48, minutes=22, seconds=40)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=3, minutes=1, seconds=0)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=100, minutes=0, seconds=0)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        creation_time = datetime.now(timezone.utc) - timedelta(hours=4, minutes=54, seconds=10)
        OpenRequests.insert_request(self.description, self.username, self.group_size, self.people_needed, self.description, 
                                    self.channel_id, creation_time)
        
        Helpers.delete_expired_requests()
        self.assertEqual(0, TestHelpers.get_all_requests_count())

    @classmethod
    def tearDownClass(cls):
        # called after all tests have run
        TestHelpers.delete_all_requests()
