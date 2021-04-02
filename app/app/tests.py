from django.test import TestCase

from app.cal import add

class CalTest(TestCase):

    def test_add_numbers(self):
        """ test that test adding two numbers together """
        self.assertEqual(add(3, 8), 11)