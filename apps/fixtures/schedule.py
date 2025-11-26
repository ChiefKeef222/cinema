import pytest
from apps.schedule.models import Hall, Session
from datetime import datetime
import zoneinfo


@pytest.fixture
def hall(db):
    """
    Fixture to create a hall instance.
    Uses update_or_create to be idempotent.
    """
    hall_obj, created = Hall.objects.update_or_create(name="Main Hall")
    return hall_obj


@pytest.fixture
def session(db, movie, hall):
    """
    Fixture to create a session instance.
    """
    utc_tz = zoneinfo.ZoneInfo("UTC")
    session_data = {
        "movie": movie,
        "hall": hall,
        "start_time": datetime(
            2030, 1, 1, 10, 0, 0, tzinfo=utc_tz
        ),  # Fixed for deterministic tests
        "price": 15.00,
    }
    # A simple create is fine here as we likely want a new session for each test
    return Session.objects.create(**session_data)
