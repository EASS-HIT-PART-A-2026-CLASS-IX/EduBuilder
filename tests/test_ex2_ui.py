from unittest.mock import Mock

import frontend.app_ex2 as app_ex2


def test_build_plan_payload_from_prompt():
    payload = app_ex2.build_plan_payload(
        "Create a beginner course on the human body with practice exercises."
    )

    assert payload["title"] == "A Beginner Course On The Human Body With Practice Exercises"
    assert payload["level"] == "Beginner"
    assert payload["is_public"] is True
    assert "practice" in payload["cues"].lower() or "example" in payload["cues"].lower()


def test_create_plan_from_prompt_posts_to_ex1_api(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status = Mock()
    fake_response.json.return_value = {
        "id": "p10",
        "title": "The Human Body",
        "goal": "Study the body",
        "cues": "Practice every day",
        "level": "Beginner",
        "is_public": True,
        "created_at": "2026-03-31T10:00:00",
    }

    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return fake_response

    monkeypatch.setattr(app_ex2.requests, "post", fake_post)

    result = app_ex2.create_plan_from_prompt("Create a beginner course on the human body.")

    assert captured["url"] == f"{app_ex2.API_URL}/plans"
    assert captured["timeout"] == 10
    assert captured["json"]["level"] == "Beginner"
    assert result["id"] == "p10"


def test_plans_to_csv_exports_expected_columns():
    csv_text = app_ex2.plans_to_csv(
        [
            {
                "id": "p1",
                "title": "The Human Body",
                "goal": "Learn the foundations",
                "cues": "Start with systems",
                "level": "Beginner",
                "is_public": True,
                "created_at": "2026-03-31T10:00:00",
            }
        ]
    )

    assert "id,title,goal,cues,level,is_public,created_at" in csv_text
    assert "The Human Body" in csv_text
