from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    return TestClient(app_module.app)


def test_get_activities_returns_activity_list(client):
    # Arrange
    activity_name = "Soccer Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert response.headers["cache-control"] == "no-store"


def test_signup_adds_participant_to_activity(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "student@example.com"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_rejects_participant_not_signed_up(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"