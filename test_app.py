import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    with app.test_client() as client:
        yield client


def test_default_route_redirect(client):
    """Test that the default route ("/") redirects to "/octocat"."""
    response = client.get("/")
    assert response.status_code == 302  # Check for redirect
    assert response.location.endswith("/octocat")  # Ensure redirection to '/octocat'


def test_octocat_gists_page(client):
    """Test fetching gists for the user 'octocat' at /octocat."""
    response = client.get("/octocat")
    assert response.status_code == 200
    assert b"Displaying gists" in response.data  # Basic check for display message
    assert b"Previous" in response.data  # Basic pagination link check
    assert b"Next" in response.data


def test_pagination_query(client):
    """Test the pagination feature with page and per_page query parameters."""
    response = client.get("/octocat?page=2&per_page=5")
    assert response.status_code == 200
    assert b"Displaying gists" in response.data  # Basic check for display message
