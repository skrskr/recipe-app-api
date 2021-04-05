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

    def test_new_user_invalid_email(self):
        """ test creating new user with invaild email """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '123445555')

    def test_new_superuser(self):
        """ test creating new super user"""
        user = get_user_model().objects.create_superuser(
            'superuser@admin.com',
            'password'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)