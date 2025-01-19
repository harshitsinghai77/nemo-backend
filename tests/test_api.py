import os

os.environ["ENV"] = "running_tests"
os.environ["TEST_SQLITE_FILE_NAME"] = "test_database.db"

import random
import unittest
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

import app.api.models.nemo
from app.api.config.database_sqlite import engine
from app.api.models.nemo import NemoSettings
from app.api.pydantic.nemo import GoogleAuth
from main import app


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        SQLModel.metadata.create_all(engine)
        print("Created test db and all the tables")
        cls.access_token = None
        cls.user_settings = None
        cls.account = None

    @classmethod
    def tearDownClass(cls):
        SQLModel.metadata.drop_all(engine)
        # os.remove(os.getenv("SQLITE_FILE_NAME"))
        print(os.getenv("SQLITE_FILE_NAME"))
        engine.dispose()  # Close all connections
        sqlite_file_name = os.getenv("TEST_SQLITE_FILE_NAME")
        if os.path.exists(sqlite_file_name):
            os.remove(sqlite_file_name)
        print("Removed test db")

    def setUp(self):
        self.client = TestClient(app)

    @pytest.mark.order(1)
    @patch("app.api.routers.nemo.get_user_payload")
    @patch("app.api.routers.nemo.check_google_user")
    @patch("app.api.routers.nemo.NemoDeta.check_user_exists")
    def test_create_user_new_user(
        self, mock_check_user_exists, mock_check_google_user, mock_get_user_payload
    ):

        # Mocking the payload returned by get_user_payload
        mock_get_user_payload.return_value = {
            "sub": "test_google_id",
            "email": "test@example.com",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/picture.png",
            "email_verified": True,
        }

        # Mocking the check_google_user to return True
        mock_check_google_user.return_value = True
        # Mocking the check_user_exists to return None (indicating new user)
        mock_check_user_exists.return_value = None

        auth = GoogleAuth(google_token="dummy_google_token")
        response = self.client.post("/nemo/login", json=auth.model_dump())

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    @pytest.mark.order(2)
    @patch("app.api.routers.nemo.check_google_user")
    @patch("app.api.routers.nemo.get_user_payload")
    def test_existing_user(self, mock_get_user_payload, mock_check_google_user):
        mock_get_user_payload.return_value = {"sub": "test_google_id"}
        mock_check_google_user.return_value = True
        # Mocking the payload returned by get_user_payload
        auth = GoogleAuth(google_token="dummy_google_token")
        response = self.client.post("/nemo/login", json=auth.model_dump())
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        TestApp.access_token = response.json()["access_token"]

    @pytest.mark.order(3)
    def test_get_user_settings(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("/nemo/settings", headers=headers)
        resp_data = response.json()
        resp_data.pop("google_id")

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(resp_data.keys(), NemoSettings().model_dump().keys())
        self.assertEqual(resp_data, NemoSettings().model_dump())
        TestApp.user_settings = resp_data

    @pytest.mark.order(4)
    def test_update_user_settings(self):
        new_settings = {
            "preference_shuffle_time": 20,
            "preference_background_color": "blue",
            "display_time": "75 : 00",
            "daily_goal": 8,
        }

        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.post(
            "/nemo/settings", json=new_settings, headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), new_settings)

        # get updated settings and check if they are updated
        response = self.client.get("/nemo/settings", headers=headers)
        resp_data = response.json()
        resp_data.pop("google_id")

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(resp_data, {**TestApp.user_settings, **new_settings})
        self.assertCountEqual(
            resp_data.keys(), {**TestApp.user_settings, **new_settings}.keys()
        )

    @pytest.mark.order(5)
    def test_get_user_image(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/user-image", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("profile_pic", response.json())
        self.assertIsInstance(response.json()["profile_pic"], str)

    @pytest.mark.order(6)
    def test_get_user_account(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/account", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        TestApp.account = response.json()

    @pytest.mark.order(7)
    def test_update_user_account(self):
        new_account = {"username": "my_username", "given_name": "John"}
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.post("nemo/account", json=new_account, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

        # only check the keys that are updated as the response will have all the keys
        resp_key = {k: v for k, v in response.json().items() if k in new_account}
        self.assertDictEqual(resp_key, new_account)
        self.assertCountEqual(resp_key.keys(), new_account.keys())

    @pytest.mark.order(8)
    def test_create_analytics(self):
        headers = {"x-auth-token": TestApp.access_token}
        total_count = 0
        for _ in range(50):
            # create a random duration from 600 to 3600
            duration = {"duration": random.randint(600, 3600)}
            total_count += duration["duration"]
            response = self.client.post(
                "nemo/analytics", json=duration, headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), dict)

        response = self.client.get("nemo/analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["total_count"], total_count)

    @pytest.mark.order(9)
    def test_get_analytics(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/analytics", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertCountEqual(
            response.json()[0].keys(), ("weekday", "total_count", "month_number")
        )
        self.assertGreaterEqual(len(response.json()), 1)

    @pytest.mark.order(10)
    def test_get_stats(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/statistics/best-day", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertCountEqual(
            response.json().keys(), ("best_day_full_date", "best_day_duration", "best_session_full_date", "best_session_duration")
        )
        self.assertGreaterEqual(len(response.json()), 1)

        response = self.client.get("nemo/statistics/some-other-stat", headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertIsInstance(response.json(), dict)
        self.assertIn("message", response.json())
        self.assertEqual(
            response.json()["message"], "Invalid category or category not found"
        )

    @pytest.mark.order(11)
    def test_create_task(self):
        headers = {"x-auth-token": TestApp.access_token}
        for i in range(20):
            # create a random duration from 600 to 3600
            duration = {
                "task_description": f"Task description {i}",
                "duration": random.randint(600, 3600),
            }
            response = self.client.post(
                "nemo/create_task", json=duration, headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), dict)

    @pytest.mark.order(12)
    def test_get_tasks(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/get-tasks", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 20)
        self.assertCountEqual(
            response.json()[0].keys(),
            (
                "id",
                "created_at",
                "duration",
                "task_description",
                "total_duration",
                "date",
            ),
        )

    @pytest.mark.order(13)
    def test_delete_task_by_id(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/get-tasks", headers=headers)

        # delete the first 10 tasks
        for task in response.json()[:10]:
            response = self.client.delete(f"nemo/tasks/{task['id']}", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(response.json(), {"success": True})

    @pytest.mark.order(14)
    def test_remove_user(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.delete("nemo/delete", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()["success"], True)

    @pytest.mark.order(15)
    def test_invalid_token(self):
        headers = {"x-auth-token": "invalid_token"}
        response = self.client.get("nemo/settings", headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response.json(), dict)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Could not validate credentials")

        headers = {"something-else": "invalid_token"}
        response = self.client.get("nemo/settings", headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "x-auth-token header missing.")

    @pytest.mark.order(16)
    def test_deleted_user_trying_to_access(self):
        headers = {"x-auth-token": TestApp.access_token}
        response = self.client.get("nemo/settings", headers=headers)

        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "No settings found for the user")

        response = self.client.post(
            "nemo/settings", headers=headers, json={"daily_goal": 10}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "No settings found for the user")

        response = self.client.get("nemo/user-image", headers=headers)
        self.assertIsNone(response.json()["profile_pic"])

        response = self.client.get("nemo/account", headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "No user account found or is empty."
        )

        response = self.client.post(
            "nemo/account", headers=headers, json={"username": "my_username"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "No user account found for the user"
        )

        response = self.client.get("nemo/analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        response = self.client.post(
            "nemo/analytics", headers=headers, json={"duration": 1000}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "User does not exist.")

        response = self.client.get("nemo/statistics/best-day", headers=headers)
        self.assertIsNone(response.json())

        response = self.client.get("nemo/statistics/current-goal", headers=headers)
        self.assertIsNone(response.json())

        response = self.client.get("nemo/statistics/some-other-stat", headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertIn("message", response.json())
        self.assertEqual(
            response.json()["message"], "Invalid category or category not found"
        )

        response = self.client.get("nemo/get-tasks", headers=headers)
        self.assertListEqual(response.json(), [])

        response = self.client.post(
            "nemo/create_task",
            headers=headers,
            json={"task_description": "Task description", "duration": 1000},
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "User does not exist.")
