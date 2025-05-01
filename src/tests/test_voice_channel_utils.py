import os
import sys
import unittest
from database.models import VoiceChannels
from datetime import datetime, timezone
from helpers_tests import TestHelpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import OpenRequests

class TestDelete(unittest.TestCase):
    channel_id = "1234567891234567890"

    def setUp(self):
        TestHelpers.delete_all_requests()

    def test_basic(self):
        creator_name = "creator_name"
        member_name = "Calvin_Corbin#1111"
        self.assertTrue(VoiceChannels.get_record_by_id(42) is None) # no group ids exist at this point
        self.assertTrue(VoiceChannels.get_joined_group_id_for_member_or_creator(member_name) is None)
        self.assertTrue(int(TestHelpers.get_all_requests_count()) == 0)
        OpenRequests.insert_request("Rust", creator_name, 1, 2, "", self.channel_id, datetime.now(timezone.utc))
        self.assertTrue(int(TestHelpers.get_all_requests_count()) == 1)

        # joined member is recognized
        group_id = TestHelpers.get_all_ids()[0][0]
        self.assertTrue(OpenRequests.user_joined_group(group_id, member_name))
        channel_id = VoiceChannels.get_record_by_id(group_id)
        self.assertTrue(channel_id == self.channel_id)
        open_group_id = VoiceChannels.get_joined_group_id_for_member_or_creator(member_name)
        self.assertTrue(open_group_id[0] == group_id)

        # sanity calling consecutively still works
        channel_id = VoiceChannels.get_record_by_id(group_id)
        self.assertTrue(channel_id == self.channel_id)

        # creator member is recognized
        open_group_id = VoiceChannels.get_joined_group_id_for_member_or_creator(creator_name)
        self.assertTrue(open_group_id[0] == group_id)

    @classmethod
    def tearDownClass(cls):
        TestHelpers.delete_all_requests()
        