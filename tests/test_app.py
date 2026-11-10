import uuid
import unittest

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.models import User
from app.utils.auth import create_access_token
from main import app


class FastApiProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({"sub": "admin"})
        cls.user_token = create_access_token({"sub": "user"})

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        from app import database

        database.engine.dispose()

    def _delete_user_by_username(self, username: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_name == username).first()
            if user is not None:
                db.delete(user)
                db.commit()
        finally:
            db.close()

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to FastAPI CRUD Application"})

    def test_hello_endpoints(self):
        response = self.client.get("/api/v1/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, world!"})

        response = self.client.get("/api/v1/hello/pepito")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, pepito!"})

    def test_login_success_and_failure(self):
        response = self.client.post("/auth/login", json={"username": "user", "password": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())
        self.assertTrue(response.json()["token"])

        response = self.client.post("/auth/login", json={"username": "user", "password": "wrong-password"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.text, "Incorrect username or password")

    def test_users_require_authentication(self):
        response = self.client.get("/api/v1/users")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Not authenticated")

    def test_authenticated_user_can_list_users(self):
        response = self.client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_admin_can_create_user_and_fetch_it(self):
        username = f"qa-{uuid.uuid4().hex[:8]}"
        payload = {
            "userName": username,
            "password": "secret123",
            "role": "USER",
            "firstName": "QA",
            "lastName": "Tester",
            "email": f"{username}@example.com",
        }

        response = self.client.post(
            "/api/v1/users",
            json=payload,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        created = response.json()
        self.assertEqual(created["userName"], username)
        self.assertEqual(created["role"], "USER")
        self.assertTrue(created["id"])

        response = self.client.get(
            f"/api/v1/users/{created['id']}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["userName"], username)

        self._delete_user_by_username(username)


if __name__ == "__main__":
    unittest.main()
