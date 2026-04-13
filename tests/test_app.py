"""
Test suite for Mergington High School Activities API
Tests all endpoints: GET / , GET /activities, POST /activities/{activity_name}/signup,
and DELETE /activities/{activity_name}/signup
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint GET /"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities returns proper structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_activities_contain_initial_participants(self, client):
        """Test that activities contain the initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "testuser@mergington.edu"
        client.post("/activities/Art%20Studio/signup?email=" + email)
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Art Studio"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup_prevention(self, client):
        """Test that student cannot sign up twice for the same activity"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Drama Club
        response2 = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Drama Club"]["participants"]
    
    def test_signup_response_format(self, client):
        """Test that signup response has the expected format"""
        response = client.post(
            "/activities/Science%20Club/signup?email=newscientist@mergington.edu"
        )
        data = response.json()
        
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "Signed up" in data["message"]


class TestRemoveEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_successful_removal(self, client):
        """Test successful removal of a participant from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
    
    def test_removal_removes_participant(self, client):
        """Test that removal actually removes the participant from the activity"""
        email = "daniel@mergington.edu"
        client.delete(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_remove_activity_not_found(self, client):
        """Test removal from non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_student_not_in_activity(self, client):
        """Test removal of student not in activity returns 404"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=notamember@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Student not found" in data["detail"]
    
    def test_remove_response_format(self, client):
        """Test that removal response has the expected format"""
        response = client.delete(
            "/activities/Drama%20Club/signup?email=mia@mergington.edu"
        )
        data = response.json()
        
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "Removed" in data["message"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_remove_workflow(self, client):
        """Test complete workflow of signing up and then removing"""
        email = "workflow@mergington.edu"
        activity = "Debate%20Team"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities["Debate Team"]["participants"]
        
        # Remove
        remove_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        activities = client.get("/activities").json()
        assert email not in activities["Debate Team"]["participants"]
    
    def test_signup_removal_and_signup_again(self, client):
        """Test that a student can sign up again after being removed"""
        email = "retry@mergington.edu"
        activity = "Programming%20Class"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email in activities["Programming Class"]["participants"]
