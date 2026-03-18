from hypothesis import HealthCheck, settings
import schemathesis
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

health_schema = schemathesis.openapi.from_asgi("/openapi.json", app).include(
    path_regex=r"^/health$",
    method="GET",
)


@health_schema.parametrize()
@settings(max_examples=3, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_health_contract(case):
    case.call_and_validate()


def test_public_courses_list_contract():
    response = client.get("/courses")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_shared_courses_contract():
    response = client.get("/courses/shared")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_courses_mine_requires_auth():
    response = client.get("/courses", params={"mine": True})
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required for mine=true"