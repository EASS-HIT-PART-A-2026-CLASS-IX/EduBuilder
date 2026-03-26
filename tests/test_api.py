from datetime import timedelta

from backend.auth import create_access_token


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_register_and_login(client):
    register_res = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpass123",
            "full_name": "New User",
        },
    )
    assert register_res.status_code == 200
    register_data = register_res.json()
    assert "access_token" in register_data
    assert register_data["token_type"] == "bearer"

    login_res = client.post(
        "/auth/login",
        json={"email": "newuser@example.com", "password": "newpass123"},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    token = login_data["access_token"]
    me_res = client.get("/me", headers=auth_headers(token))
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "newuser@example.com"
    assert me_data["role"] == "user"


def test_protected_routes_without_token(client):
    res = client.get("/me")
    assert res.status_code == 401

    res2 = client.get("/courses/my")
    assert res2.status_code == 401

    res3 = client.post(
        "/courses",
        json={
            "title": "Auth Required",
            "content": "This should fail without a token",
            "is_public": True,
        },
    )
    assert res3.status_code == 401


def test_me_with_token(client, user_token):
    res = client.get("/me", headers=auth_headers(user_token))
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"


def test_courses_crud_flow(client, user_token):
    create_res = client.post(
        "/courses",
        json={
            "title": "Intro to AI",
            "content": "Basics of AI content",
            "is_public": True,
        },
        headers=auth_headers(user_token),
    )
    assert create_res.status_code == 200
    created = create_res.json()
    course_id = created["id"]
    assert created["title"] == "Intro to AI"
    assert created["owner_id"] is not None

    list_res = client.get("/courses")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["id"] == course_id for item in items)

    detail_res = client.get(f"/courses/{course_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Intro to AI"

    update_res = client.put(
        f"/courses/{course_id}",
        json={
            "title": "Intro to AI Updated",
            "content": "Updated AI content",
            "is_public": False,
        },
        headers=auth_headers(user_token),
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Intro to AI Updated"
    assert updated["is_public"] is False

    mine_res = client.get("/courses/my", headers=auth_headers(user_token))
    assert mine_res.status_code == 200
    assert any(item["id"] == course_id for item in mine_res.json())

    delete_res = client.delete(
        f"/courses/{course_id}",
        headers=auth_headers(user_token),
    )
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "success"

    missing_res = client.get(f"/courses/{course_id}")
    assert missing_res.status_code == 404


def test_private_course_hidden_from_others(client, user_token):
    create_res = client.post(
        "/courses",
        json={
            "title": "Private Course",
            "content": "Secret content",
            "is_public": False,
        },
        headers=auth_headers(user_token),
    )
    assert create_res.status_code == 200
    course_id = create_res.json()["id"]

    anonymous_res = client.get(f"/courses/{course_id}")
    assert anonymous_res.status_code == 403


def test_token_scope_missing_on_admin_route(client, test_user):
    login_res = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_res.json()["access_token"]

    res = client.get("/admin/only", headers=auth_headers(token))
    assert res.status_code == 403
    assert "Missing scope" in res.json()["detail"]


def test_invalid_login(client, test_user):
    res = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrong-password"},
    )
    assert res.status_code == 401


def test_expired_token_rejected(client):
    expired = create_access_token(
        {"sub": "expired@example.com", "role": "user"},
        expires_delta=timedelta(minutes=-1),
    )
    res = client.get("/me", headers=auth_headers(expired))
    assert res.status_code == 401


def test_admin_route_forbidden_for_user(client, user_token):
    res = client.get("/admin/only", headers=auth_headers(user_token))
    assert res.status_code == 403


def test_admin_route_allows_admin(client, admin_user):
    login_res = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]

    res = client.get("/admin/only", headers=auth_headers(admin_token))
    assert res.status_code == 200
    assert res.json()["status"] == "admin_verified"