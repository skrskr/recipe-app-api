from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")

class PublicTagsApiTests(TestCase):
    """ test the public available tags api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ test that login is required for retrieving tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """ test the autherized user tag api """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_retrieving_tags(self):
        """ test retrieving tags"""
        Tag.objects.create(user = self.user, name="Tag1")
        Tag.objects.create(user = self.user, name="Tag2")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ test that tags returned are for authenticated user """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        Tag.objects.create(user = user2, name="New Tag")
        tag = Tag.objects.create(user = self.user, name="New Tag2")
        
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_tag_created_sucessful(self):
        """ test that tag created sucessfully"""
        payload = {'name': "new tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ test creating tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """ Test filtering tags by assigned recipes"""
        tag1 = Tag.objects.create(user = self.user, name="tag1")
        tag2 = Tag.objects.create(user = self.user, name="tag2")

        recipe1 = Recipe.objects.create(
            title="Title1",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe1.tags.add(tag1)
        recipe2 = Recipe.objects.create(
            title="Title2",
            time_minutes=30,
            price=5.00,
            user = self.user
        )

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """ Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user = self.user, name="tag1")
        Tag.objects.create(user = self.user, name="tag2")

        recipe1 = Recipe.objects.create(
            title="Title1",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title="Title2",
            time_minutes=30,
            price=5.00,
            user = self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
