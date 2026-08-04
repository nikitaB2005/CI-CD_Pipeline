import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_returns_up(client):
    """/health should report the service as UP."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"


def test_dashboard_page_loads(client):
    """/ should render the dashboard HTML successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Build Information" in response.data


def test_api_build_info_returns_json(client):
    """/api/build-info should return a JSON response."""
    response = client.get("/api/build-info")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_build_info_has_required_fields(client):
    """The build info JSON must contain every field the dashboard displays."""
    response = client.get("/api/build-info")
    data = response.get_json()
    required_fields = [
        "application", "environment", "version", "branch",
        "commit", "docker_image", "build_number",
        "pipeline_status", "deployment_time", "pods", "server",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_unknown_route_returns_404(client):
    """Unknown routes should not silently succeed."""
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404