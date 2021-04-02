from django.test import TestCase

from app.cal import add, subtract

class CalTest(TestCase):

    def test_add_numbers(self):
        """ test that test adding two numbers together """
        self.assertEqual(add(3, 8), 11)

    def test_subtract_numbers(self):
        """ test that test subtracting two numbers and return value"""
        self.assertEqual(subtract(8,5), 3)