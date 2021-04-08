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

    def test_create_basic_recipe(self):
        """ test creating basic recipe"""
        payload = {
            'title': 'recipe 1',
            'time_minutes': 3,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ test creating recipe with tags"""
        tag1 = sample_tag(user = self.user, name="Tag1")
        tag2 = sample_tag(user = self.user, name="Tag2")

        payload = {
            'title': 'recipe 1',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 3,
            'price': 3.39
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user = self.user, name="Ingredient1")
        ingredient2 = sample_ingredient(user = self.user, name="Ingredient2")

        payload = {
            'title': 'recipe 1',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 3,
            'price': 3.39
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """ test partial update recipe """
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))

        new_tag = sample_tag(user = self.user, name = "Tag2")

        payload = {'title': 'new recipe', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """ test updating recipe with update"""
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))

        payload = {'title': 'new recipe', 'price': 3.00, 'time_minutes': 4}

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)