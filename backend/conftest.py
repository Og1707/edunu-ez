import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """
    Fixture global que provee una instancia limpia de APIClient de Django REST Framework.
    """
    return APIClient()
