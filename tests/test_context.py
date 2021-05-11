import unittest
from typing import List

from disctools import TargetContext as TestCtx

class MockUser:
    def __init__(self, top_role: int):
        self.top_role = top_role
        self._received = None

    def send(self, *args, **kwargs):
        self._received = (args, kwargs)

class MockGuild:
    def __init__(self, owner: MockUser):
        self.owner = owner

class MockMessage:
    def __init__(self, author: MockUser, mentions: List[MockUser], guild: MockGuild):
        self.author = author
        self.mentions = mentions
        self.guild = guild
        self._state = None

class ContextTest(unittest.TestCase):
    def setUp(self):
        self.User7 = MockUser(7) # Mentioned 1, Admin above owner (A)(U7)
        self.User4 = MockUser(4) # Mentioned 2 (T)(U4)
        self.User6 = MockUser(6) # Owner (O)(U6)
        self.User5 = MockUser(5) # Mod (M)(U5)
        self.Guild6 = MockGuild(self.User6)
        self.Message65 = MockMessage(self.User6, [self.User5], self.Guild6) # Ban, Kick etc. by owner
        self.Message56 = MockMessage(self.User5, [self.User6], self.Guild6) # Moderator trying to kick, ban Owner
        self.Message44 = MockMessage(self.User4, [self.User7, self.User4], self.Guild6) # trainee mod targeting admin and mentioning self
        self.Message76 = MockMessage(self.User7, [self.User6], self.Guild6) # Admin kicking owner
        self.Message67 = MockMessage(self.User6, [self.User7], self.Guild6) # Owner kicking Admin
        self.Context1 = TestCtx(message=self.Message65, prefix="a") # Case 1
        self.Context2 = TestCtx(message=self.Message56, prefix="a") # 2 ...
        self.Context3 = TestCtx(message=self.Message44, prefix="a")
        self.Context4 = TestCtx(message=self.Message76, prefix="a")
        self.Context5 = TestCtx(message=self.Message67, prefix="a")

    def test_above(self):
        self.assertTrue(self.Context1.is_author_above()[0]) # U6(O) > U5
        self.assertFalse(self.Context2.is_author_above()[0])
        self.assertFalse(self.Context3.is_author_above()[0])
        self.assertFalse(self.Context4.is_author_above()[0])
        self.assertTrue(self.Context5.is_author_above()[0])

    def test_is_target(self):
        self.assertFalse(self.Context1.is_author_target)
        self.assertFalse(self.Context2.is_author_target)
        self.assertTrue(self.Context3.is_author_target)

        self.assertFalse(self.Context1.is_user_target(self.User7))
        self.assertFalse(self.Context2.is_user_target(self.User7))
        self.assertTrue(self.Context3.is_user_target(self.User7))

    def test_target_prop(self):
        self.Context1.targets = self.User4
        self.assertIsInstance(self.Context1.targets, list)
        self.assertIn(self.User4, self.Context1.targets)
        self.assertNotIn(self.User5, self.Context1.targets)

    def test_target_order(self):
        self.Context1.targets = [self.User5, self.User7, self.User4]
        self.assertIsInstance(self.Context1.targets, list)
        self.assertNotIsInstance(self.Context1.targets[0], (list, tuple))
        self.assertIsInstance(self.Context1.targets[0], MockUser)
        self.assertEqual(self.Context1.targets[1], self.User7, "Target Order preservation failed")

if __name__ == "__main__":
    unittest.main()
