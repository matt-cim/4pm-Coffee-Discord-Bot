import os
import sys
import unittest
from datetime import datetime, timezone
from helpers_tests import TestHelpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import OpenRequests

class TestJoiningGroups(unittest.TestCase):
    channel_id = "1234567891234567890"

    def setUp(self):
        # refresh table before each test
        TestHelpers.delete_all_requests()

    def test_join_1(self):
        total_requests = 32
        users = ["chad_wick", "USER", "89452", "discord"]

        for i in range(total_requests):
            OpenRequests.insert_request("Marvel Rivals", "voidptr", i, i, " desc ", self.channel_id, datetime.now(timezone.utc))

        ids = [id_tup[0] for id_tup in TestHelpers.get_all_ids()] # unravel from tuples
        self.assertEqual(total_requests, TestHelpers.get_all_requests_count())
        # double check corresponding id in open_voice_channels is being set correctly
        vc_group_ids = [id_tup[0] for id_tup in TestHelpers.get_all_open_group_ids()]
        self.assertEqual(ids, vc_group_ids)

        OpenRequests.user_joined_group(str(ids[0]), users[0]) # people_needed -> -1 (rare edge case)
        OpenRequests.user_joined_group(str(ids[1]), users[1]) # people_needed -> 0
        id = str(ids[2])
        OpenRequests.user_joined_group(id, users[2]) # people_needed -> 1 (no delete)
        # user now stored as member of group
        self.assertEqual([users[2]], TestHelpers.get_members_for_group(id))
        id = str(ids[3])
        OpenRequests.user_joined_group(id, users[3]) # people_needed -> 2 (no delete)
        self.assertEqual([users[3]], TestHelpers.get_members_for_group(id))

        self.assertEqual(total_requests - 2, TestHelpers.get_all_requests_count())

    def test_join_2(self):
        group_one_people_needed = 4
        group_two_people_needed = 21
        OpenRequests.insert_request("Pokemon", "max ruth", 7, group_one_people_needed, "puma\n", self.channel_id, datetime.now(timezone.utc))
        OpenRequests.insert_request("Just Chatting", "LEO", 21, group_two_people_needed, "", self.channel_id, datetime.now(timezone.utc))

        ids = [id_tup[0] for id_tup in TestHelpers.get_all_ids()]
        self.assertEqual(2, TestHelpers.get_all_requests_count())

        id_1 = str(ids[0])
        for i in range(group_one_people_needed):
            OpenRequests.user_joined_group(id_1, str(i))
            if i == group_one_people_needed - 1: # last needed user join
                self.assertEqual(1, TestHelpers.get_all_requests_count())
            else:
                self.assertEqual(2, TestHelpers.get_all_requests_count())
                # no duplication of members and added every iteration
                members = TestHelpers.get_members_for_group(id_1)
                self.assertEqual(i + 1, len(members))
                self.assertTrue(len(members) == len(set(members)))

        id_2 = str(ids[1])
        for j in range(group_two_people_needed):
            OpenRequests.user_joined_group(id_2, str(j))
            if j == group_two_people_needed - 1:
                self.assertEqual(0, TestHelpers.get_all_requests_count())
            else:
                # record should exist until no more people needed
                self.assertEqual(1, TestHelpers.get_all_requests_count())
                members = TestHelpers.get_members_for_group(id_2)
                self.assertEqual(j + 1, len(members))
                self.assertTrue(len(members) == len(set(members)))

    def test_join_3(self):
        creator = "creator's_username"
        OpenRequests.insert_request("It takes two", creator, 7, 50, "", self.channel_id, datetime.now(timezone.utc))

        id = TestHelpers.get_all_ids()[0][0]
        # group creator cannot join their own group
        self.assertFalse(OpenRequests.user_joined_group(id, creator))

        self.assertTrue(OpenRequests.user_joined_group(id, "new user"))
        self.assertTrue(OpenRequests.user_joined_group(id, "rando"))
        self.assertTrue(OpenRequests.user_joined_group(id, "Existing"))
        self.assertFalse(OpenRequests.user_joined_group(id, "Existing"))
        self.assertFalse(OpenRequests.user_joined_group(id, "rando"))
        self.assertTrue(OpenRequests.user_joined_group(id, "again new"))
        self.assertFalse(OpenRequests.user_joined_group(id, "new user"))
        self.assertTrue(OpenRequests.user_joined_group(id, "ban"))
        self.assertFalse(OpenRequests.user_joined_group(id, "ban"))
        self.assertFalse(OpenRequests.user_joined_group(id, "ban"))
        self.assertFalse(OpenRequests.user_joined_group(id, creator))

    @classmethod
    def tearDownClass(cls):
        # don't want to intefere with other tests
        TestHelpers.delete_all_requests()
