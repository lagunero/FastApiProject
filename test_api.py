import requests
import json
import sys

BASE_URL = "http://localhost:9080"

def test_login():
    print("\n1. Testing login endpoint...")
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "user", "password": "password"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    if response.status_code == 200:
        token = response.json().get("token")
        return token
    return None

def test_hello(token):
    print("\n2. Testing /api/v1/hello endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/hello", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_hello_with_name(token, name="World"):
    print(f"\n3. Testing /api/v1/hello/{name} endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/hello/{name}", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_get_all_users(token):
    print("\n4. Testing GET /api/v1/users endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/users", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   Found {len(users)} users")
        for user in users[:2]:
            first_name = user.get('firstName')
            last_name = user.get('lastName')
            email = user.get('email')
            print(f"   - {first_name} {last_name} ({email})")
    else:
        print(f"   Response: {response.json()}")

def test_create_user(token):
    print("\n5. Testing POST /api/v1/users endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    new_user = {
        "firstName": "TestUser",
        "lastName": "TestLast",
        "email": "test@example.com",
        "birthDate": "1990-01-01"
    }
    response = requests.post(f"{BASE_URL}/api/v1/users", json=new_user, headers=headers)
    print(f"   Status: {response.status_code}")
    response_data = response.json()
    print(f"   Response: {response_data}")
    if response.status_code == 200:
        return response_data.get("id")
    return None

def test_get_user_by_id(token, user_id):
    print(f"\n6. Testing GET /api/v1/users/{user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/users/{user_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_update_user(token, user_id):
    print(f"\n7. Testing PUT /api/v1/users/{user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "firstName": "UpdatedUser",
        "lastName": "UpdatedLast",
        "email": "updated@example.com",
        "birthDate": "1990-05-05"
    }
    response = requests.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_delete_user(token, user_id):
    print(f"\n8. Testing DELETE /api/v1/users/{user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/v1/users/{user_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_unauthorized():
    print("\n9. Testing unauthorized access (no token)...")
    response = requests.get(f"{BASE_URL}/api/v1/users")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def run_tests():
    """Entrypoint used by pyproject script `test-api`.
    Ejecuta la secuencia de pruebas de integración de ejemplo.
    """
    try:
        token = test_login()
        if token:
            test_hello(token)
            test_hello_with_name(token, "FastAPI")
            test_get_all_users(token)
            user_id = test_create_user(token)
            if user_id:
                test_get_user_by_id(token, user_id)
                test_update_user(token, user_id)
                test_delete_user(token, user_id)
            test_unauthorized()
            return 0
        else:
            print("Failed to obtain token!")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
