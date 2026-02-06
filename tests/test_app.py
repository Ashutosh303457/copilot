"""Tests for the Mergington High School Activities API."""
import pytest
from fastapi import status


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK

    def test_get_activities_returns_dict(self, client):
        """Test that getting activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_activities(self, client):
        """Test that activities response contains expected activity names."""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Science Club",
            "Debate Team",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_details in activities.values():
            for field in required_fields:
                assert field in activity_details


class TestSignUp:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Signed up" in response.json()["message"]

    def test_signup_updates_participants(self, client):
        """Test that signup adds the student to participants."""
        email = "newemail@mergington.edu"
        # Sign up the student
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_email_fails(self, client):
        """Test that signing up with an email already in an activity fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client):
        """Test that signup increments the participant count."""
        email = "counter@mergington.edu"
        activities_before = client.get("/activities").json()
        count_before = len(activities_before["Chess Club"]["participants"])

        client.post(f"/activities/Chess Club/signup?email={email}")

        activities_after = client.get("/activities").json()
        count_after = len(activities_after["Chess Club"]["participants"])

        assert count_after == count_before + 1


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity."""
        # First sign up
        email = "unregister@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")

        # Now unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the student from participants."""
        email = "removeMe@mergington.edu"
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        # Verify they're added
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")

        # Verify they're removed
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_not_signed_up_fails(self, client):
        """Test that unregistering a student not signed up fails."""
        email = "notmemeber@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from a nonexistent activity fails."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decrements the participant count."""
        email = "decrementcount@mergington.edu"
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        activities_before = client.get("/activities").json()
        count_before = len(activities_before["Chess Club"]["participants"])

        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")

        # Verify count decreased
        activities_after = client.get("/activities").json()
        count_after = len(activities_after["Chess Club"]["participants"])

        assert count_after == count_before - 1


class TestRoot:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [
            status.HTTP_301_MOVED_PERMANENTLY,
            status.HTTP_302_FOUND,
            status.HTTP_307_TEMPORARY_REDIRECT,
            status.HTTP_308_PERMANENT_REDIRECT,
        ]
        assert "/static/index.html" in response.headers.get("location", "")
