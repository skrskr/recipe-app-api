from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

    def test_create_user_with_email_successfully(self):
        """ test creating user with email success"""
        email = "mohamed@mail.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test new user email is normalized"""
        email = "mohamed@MAIL.COM"
        user = get_user_model().objects.create_user(email, '123456789')

        self.assertEqual(user.email, email.lower())