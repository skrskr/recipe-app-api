from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """ test the public avialabe ingredients api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ test that login is required for retriving ingredieents"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ test the autherized user ingredients api """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)

    def test_retrieving_ingredients(self):
        """ test retrieving ingredients"""
        Ingredient.objects.create(user = self.user, name = "ingredient1")
        Ingredient.objects.create(user = self.user, name = "ingredient2")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("-name")

        serializer = IngredientSerializer(ingredients, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ test that ingredients limited for authenticated user """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'Pass123'
        )
        Ingredient.objects.create(user = user2, name = "ingredient1")
        
        ingredient = Ingredient.objects.create(user = self.user, name = "ingredient1")
        
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)