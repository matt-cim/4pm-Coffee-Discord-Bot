import os
import sys
import unittest
from decimal import Decimal, ROUND_HALF_UP
from helpers_tests import TestHelpers
# path only updated for the current runtime this is executed in
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import UserRatings, GameRatings


class TestUserRating(unittest.TestCase):

    def avg_lst(lst) -> int:
        return sum(lst) / len(lst)

    def setUp(self):
        # refresh tables before each test
        TestHelpers.delete_all_ratings()

    def test_user(self):
        usr_1 = "michaelMonero"
        usr1_ratings = [1,2,3,4,5]
        self.assertEqual(None, UserRatings.get_rating("i_do_not_exist"))

        UserRatings.insert_rating(usr_1, usr1_ratings[0]) # expecting whole numbers 1-5
        self.assertEqual(usr1_ratings[0], UserRatings.get_rating(usr_1))
        UserRatings.insert_rating(usr_1, usr1_ratings[1])
        sliced = usr1_ratings[0:2]
        self.assertEqual(TestUserRating.avg_lst(sliced), UserRatings.get_rating(usr_1))
        
        usr_2 = "LOL"
        UserRatings.insert_rating(usr_2, 5)
        self.assertEqual(5, UserRatings.get_rating(usr_2))
        self.assertEqual(5, UserRatings.get_rating(usr_2))
        UserRatings.insert_rating(usr_2, 1)
        UserRatings.insert_rating(usr_2, 2)
        self.assertEqual((Decimal(5+1+2) / Decimal(3)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), 
                         UserRatings.get_rating(usr_2))

        UserRatings.insert_rating(usr_1, usr1_ratings[2])
        sliced = usr1_ratings[0:3]
        self.assertEqual(TestUserRating.avg_lst(sliced), UserRatings.get_rating(usr_1))
        UserRatings.insert_rating(usr_1, usr1_ratings[3])
        sliced = usr1_ratings[0:4]
        self.assertEqual(TestUserRating.avg_lst(sliced), UserRatings.get_rating(usr_1))
        UserRatings.insert_rating(usr_1, usr1_ratings[4])
        sliced = usr1_ratings[0:5]
        self.assertEqual(TestUserRating.avg_lst(sliced), UserRatings.get_rating(usr_1))

        self.assertEqual(None, UserRatings.get_rating("lol"))

    def test_game(self):
        game_1 = "Outlast Trials"
        game1_ratings = [2,4,3,5,3]
        game_2 = "GTA 42"
        game2_ratings = [1,5,2]
        self.assertEqual(None, GameRatings.get_rating("Pokemon"))
        self.assertEqual(None, GameRatings.get_rating("Bones"))

        GameRatings.insert_rating(game_1, game1_ratings[0])
        self.assertEqual(game1_ratings[0], GameRatings.get_rating(game_1))
        GameRatings.insert_rating(game_2, game2_ratings[0])
        self.assertEqual(game2_ratings[0], GameRatings.get_rating(game_2))
        
        GameRatings.insert_rating(game_1, game1_ratings[1])
        sliced = game1_ratings[0:2]
        self.assertEqual(TestUserRating.avg_lst(sliced), GameRatings.get_rating(game_1))
        GameRatings.insert_rating(game_2, game2_ratings[1])
        sliced = game2_ratings[0:2]
        self.assertEqual(TestUserRating.avg_lst(sliced), GameRatings.get_rating(game_2))

        GameRatings.insert_rating(game_1, game1_ratings[2])
        sliced = game1_ratings[0:3]
        self.assertEqual(TestUserRating.avg_lst(sliced), GameRatings.get_rating(game_1))
        GameRatings.insert_rating(game_2, game2_ratings[2])
        sliced = game2_ratings[0:3]
        self.assertEqual((Decimal(1+5+2) / Decimal(3)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), 
                         GameRatings.get_rating(game_2))

        GameRatings.insert_rating(game_1, game1_ratings[3])
        sliced = game1_ratings[0:4]
        self.assertEqual(TestUserRating.avg_lst(sliced), GameRatings.get_rating(game_1))

        GameRatings.insert_rating(game_1, game1_ratings[4])
        sliced = game1_ratings[0:5]
        self.assertEqual((Decimal(2+4+3+5+3) / Decimal(5)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), 
                         GameRatings.get_rating(game_1))

    @classmethod
    def tearDownClass(cls):
        # called after all tests have run
        TestHelpers.delete_all_ratings()
