from http import client
from urllib import response
from fastapi.testclient import TestClient
from labelu.main import app

client = TestClient(app)


class TestClassUserRouter:
    def test_user_signup_successful(self):
        data = {"email": "labelu@example.com", "password": "labelU@123"}
        response = client.post("/users/signup", json=data)
        assert response.status_code == 201

    def test_user_login_sucessful(self):
        data = {"email": "labelu@example.com", "password": "labelU@123"}
        response = client.post("/users/login", json=data)
        assert response.status_code == 200
        assert response.json()["data"]["token"] == "token"

    def test_user_logout_sucessful(self):
        header = {"token": "token"}
        response = client.post("/users/logout", headers=header)
        assert response.status_code == 200
        assert response.json()["data"]["msg"] == "succeeded"
