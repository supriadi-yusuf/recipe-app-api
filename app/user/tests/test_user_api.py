"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# reverse(app_name:url_name)
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    """Create and return new user"""
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTest(TestCase):
    """test public feature of user API."""

    def setUp(self) -> None:
        self.client = APIClient()

        self.payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

    def test_create_user_success(self):
        """Test creating a user successfully."""
        result = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=self.payload['email'])

        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', result.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        create_user(**self.payload)
        result = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passsword_too_short(self):
        """Test an error is returned if password is less than 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test Name',
        }

        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        create_user(**self.payload)

        payload = {
            'email': self.payload['email'],
            'password': self.payload['password']
        }
        result = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credential is invalid"""
        create_user(**self.payload)

        payload = {'email': self.payload['email'], 'password': 'badpass123'}
        result = self.client.post(TOKEN_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', result.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password return an error"""
        create_user(**self.payload)

        payload = {'email': self.payload['email'], 'password': ''}
        result = self.client.post(TOKEN_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', result.data)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.client = APIClient()

        self.payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        self.user = create_user(**self.payload)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test post is not allowed for the me endpoint"""
        result = self.client.post(ME_URL, {})
        self.assertEqual(
            result.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test_update_user_profile(self):
        """Test updating the user profile for current authenticated user."""
        payload = {'name': 'Updated name', 'password': 'newpass1234'}
        result = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
