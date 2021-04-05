from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("users:create")

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test user public api """

    def setUp(self):
        self.client = APIClient()
    
    def test_create_valid_user_success(self):
        """ test creating user with valid paylod is success """
        payload = {
            'email': 'test@test.test',
            'password': 'test123',
            'name': 'test name' 
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ test creating user already exists failed """
        payload = {
            'email': 'test@test.test',
            'password': 'test123'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ test that the password must be more than 5 characters """
        payload = {
            'email': 'test@test.test',
            'password': 'pw'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)
