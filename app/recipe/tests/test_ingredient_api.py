from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe

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

    def test_ingredient_created_sucessfully(self):
        """ test that ingredient created sucessfully """
        payload = {'name': "Ingreident 1"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()

        self.assertTrue(exists)
        
    def test_create_ingredient_invalid(self):
        """ test create  ingredient invalid payload"""
        payload = {'name': ""}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """ Test filtering ingredients by assigned recipes"""
        ingredient1 = Ingredient.objects.create(user = self.user, name="Ingredient1")
        ingredient2 = Ingredient.objects.create(user = self.user, name="Ingredient2")

        recipe1 = Recipe.objects.create(
            title="Title1",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe1.ingredients.add(ingredient1)
        recipe2 = Recipe.objects.create(
            title="Title2",
            time_minutes=30,
            price=5.00,
            user = self.user
        )

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """ Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user = self.user, name="Ingredient1")
        Ingredient.objects.create(user = self.user, name="Ingredient2")

        recipe1 = Recipe.objects.create(
            title="Title1",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title="Title2",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)