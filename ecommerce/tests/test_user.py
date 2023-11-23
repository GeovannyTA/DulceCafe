import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_user_creation():
    User.objects.create_user(
        password="1234",
        username="test",
        first_name="test",
        last_name="test",
        email=12,
        is_staff=False,
        is_active=True,
    )
    assert User.objects.count() == 1