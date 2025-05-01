import os
import sys
import unittest
from datetime import datetime, timezone
from helpers_tests import TestHelpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import OpenRequests

class TestDelete(unittest.TestCase):
    channel_id = "1234567891234567890"

    def setUp(self):
        TestHelpers.delete_all_requests()

    def test_delete_1(self):
        self.assertFalse(OpenRequests.delete_open_group("user"))
        OpenRequests.insert_request("Pokemon", "not_user", 5, 5, "", self.channel_id, datetime.now(timezone.utc))
        self.assertFalse(OpenRequests.delete_open_group("user")) # wrong username
        self.assertTrue(OpenRequests.delete_open_group("not_user"))
        self.assertFalse(OpenRequests.delete_open_group("not_user")) # already deleted

    def test_delete_2(self):
        OpenRequests.insert_request("Madden 25", "Mahomes", 22, 1, "", self.channel_id, datetime.now(timezone.utc))
        OpenRequests.insert_request("Bluey", "dog_lover_32", 4, 4, "random", self.channel_id, datetime.now(timezone.utc))
        self.assertTrue(OpenRequests.delete_open_group("Mahomes"))
        self.assertTrue(OpenRequests.delete_open_group("dog_lover_32"))
        self.assertFalse(OpenRequests.delete_open_group("not_user"))
        OpenRequests.insert_request("Hogwart's Legacy", "trial&error", 2, 2, "", self.channel_id, datetime.now(timezone.utc))
        self.assertTrue(OpenRequests.delete_open_group("trial&error"))
        self.assertFalse(OpenRequests.delete_open_group("Mahomes"))

    @classmethod
    def tearDownClass(cls):
        TestHelpers.delete_all_requests()
        