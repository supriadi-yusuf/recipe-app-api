"""
Test for django admin page ( list objects page,
modify data page, add new data page).
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test from django admin page."""

    # setup data for testing
    # in this case name of function doesn't follow snake case convention.
    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    # test user list page on django admin
    def test_user_list_page(self):
        """Test if list users page works"""

        # reverse documentation :
        # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#reversing-admin-urls
        url = reverse('admin:core_user_changelist')

        result = self.client.get(url)

        self.assertContains(result, self.user.name)
        self.assertContains(result, self.user.email)

    # test user update page on django admin
    def test_edit_user_page(self):
        """Test if edit user page works"""

        url = reverse('admin:core_user_change', args=[self.user.id])
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)

    def test_create_user_page(self):
        """Test if create user page works"""
        url = reverse('admin:core_user_add')
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)
