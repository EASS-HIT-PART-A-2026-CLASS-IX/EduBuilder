from fastapi.testclient import TestClient

from backend.main_ex1 import app, COURSES


client = TestClient(app)


def setup_function():
    COURSES.clear()


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_full_crud_flow():
    create_res = client.post(
        "/courses",
        json={
            "title": "Intro to AI",
            "content": "Basic concepts",
            "is_public": True,
        },
    )
    assert create_res.status_code == 200
    created = create_res.json()
    course_id = created["id"]

    list_res = client.get("/courses")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = client.get(f"/courses/{course_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Intro to AI"

    update_res = client.put(
        f"/courses/{course_id}",
        json={
            "title": "Intro to AI Updated",
            "content": "Updated concepts",
            "is_public": False,
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Intro to AI Updated"
    assert update_res.json()["is_public"] is False

    delete_res = client.delete(f"/courses/{course_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "success"

    missing_res = client.get(f"/courses/{course_id}")
    assert missing_res.status_code == 404
