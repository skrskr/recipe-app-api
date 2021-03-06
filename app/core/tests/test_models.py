from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email = 'mohamed@mail.com', password = 'Pass123'):
    """ create sample user """
    return get_user_model().objects.create_user(email, password)

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

    def test_tag_str(self):
        """ test that tag str representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name="Tag1"
        )
        self.assertEqual(str(tag), tag.name)
    
    def test_ingredient_str(self):
        """ test that ingredient str representation"""
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name="Ingredient 1"
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ test that recipe str representation"""
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = "Recipe 1",
            time_minutes = 5,
            price = 6.40
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ test that image is saved in the correct location """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)