import unittest
from . import Bisac

class TestBisac(unittest.TestCase):
    def setUp(self):
        self.bisac=Bisac()
    def test_code(self):
        self.assertEqual(self.bisac.code('Religion'),'REL000000')
    