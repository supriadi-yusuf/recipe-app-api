"""
Test custom django management commands
"""
from unittest.mock import patch, MagicMock
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# mock check behaviour
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self,
                               # because we use @patch to mock check,
                               # so patched_check argument exists
                               patched_check: MagicMock
                               ):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    # mock/replace time.sleep method behaviour with magic mock
    @patch('time.sleep')
    def test_wait_for_db_delay(self,
                               # because we use @patch to mock sleep,
                               # so patched_sleep argument exists
                               patch_sleep: MagicMock,
                               # because we use @patch to mock check,
                               # so patched_check argument exists
                               patched_check: MagicMock
                               ):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
