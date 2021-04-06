from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token")
ME_URL = reverse("users:me")

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
            'password': 'pw',
            'name': 'Test'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ test that token is created for user """
        payload = {
            'email': 'test@test.test',
            'password': 'test123',
            'name': "Test name"
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentails(self):
        """ test that token is not created if invalid credentails given"""
        create_user(email="test@test.com", password="123456", name="Test name")
        payload = {
            'email': 'test@test.test',
            'password': 'wrong'
        }

        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ test that token is not created for not exist user"""
        payload = {
            'email': 'test@test.test',
            'password': 'wrong'
        }

        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ test that email and password required"""
        payload = {
            'email': 'test',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrive_user_unauthorized(self):
        """ Test that authentication is required """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ Test API requests that requried authentication """
    
    def setUp(self):
        self.user = create_user(
            email = 'test@test.com',
            password = 'password',
            name = "name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_sucess(self):
        """ test retrieving profile for logged in user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_method_not_allowed(self):
        """ test post method not allowed on the me url """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_sucess(self):
        """ test update profile success for authenticated user"""
        payload = {
            'name': 'new name',
            'password': 'password123'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
