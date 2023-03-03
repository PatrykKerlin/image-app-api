"""
Test custom Django management commands.
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model

from core.models import Tier


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands without model manipulations."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database is ready."""
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = (
            [Psycopg2OpError] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])


class CommandDatabaseTests(TestCase):
    """Test commands with model manipulations."""

    def test_create_base_setup(self):
        """Test adding basic data to database."""

        call_command("create_base_setup")
        names = Tier.objects.values_list("name", flat=True)
        users = get_user_model().objects.values_list("username", flat=True)

        self.assertEqual(len(names), 3)
        self.assertEqual(set(names), {"Basic", "Premium", "Enterprise"})
        self.assertEqual(len(users), 1)
        self.assertEqual(set(users), {"admin"})
