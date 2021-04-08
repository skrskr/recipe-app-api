from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name = "Tag1"):
    """ create sample tag and return it """
    return Tag.objects.create(user = user, name = name)

def sample_ingredient(user, name = "Ingredient1"):
    """ create and return sample ingredient"""
    return Ingredient.objects.create(user = user, name = name)

def sample_recipe(user, **params):
    """ create sample recipe object"""
    defaults = {
        'title': 'Recipe1',
        'time_minutes': 5,
        'price': 4.50
    }
    defaults.update(params)

    return Recipe.objects.create(user = user, **defaults)


class PublicRecipeApiTests(TestCase):
    """ test unauthenticated recipe apis"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ test that login is required for retrieving recipes"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTests(TestCase):
    """ test autherized recipe api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)

    def test_retrieving_recipes(self):
        """ test retriving recipes list"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ test that recipes limited for authenticated user"""

        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        sample_recipe(user2)
        recipe = sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)
        
    def test_view_recipe_detail(self):
        """ test view recipe detail """
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))
        recipe.ingredients.add(sample_ingredient(user = self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)