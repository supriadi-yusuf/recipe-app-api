"""
this is django command to wait for the database to be available.
this command can be executed by django with : python manage.py wait_for_db
"""

import time

from psycopg2 import OperationalError as Psycopg2Error

from typing import Any

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database until the database is ready"""

    def handle(self, *args: Any, **options: Any) -> str | None:
        """overwrite method handle"""
        self.stdout.write('Waiting for database ...')
        db_up: bool = False
        while db_up is False:
            try:
                # check if database ready
                # if db is not ready it will raise exception
                self.check(databases=['default'])

                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second ...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
