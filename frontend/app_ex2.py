import csv
import io
import os
import re
from datetime import datetime

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

CARD_COLORS = [
    "linear-gradient(135deg, #1f78c1 0%, #3ca0f0 100%)",
    "linear-gradient(135deg, #f57c00 0%, #ff9f1c 100%)",
    "linear-gradient(135deg, #0b1f3a 0%, #174a82 100%)",
]

LEVEL_KEYWORDS = {
    "beginner": "Beginner",
    "intro": "Beginner",
    "easy": "Beginner",
    "intermediate": "Intermediate",
    "mid": "Intermediate",
    "advanced": "Advanced",
    "expert": "Advanced",
}

st.set_page_config(
    page_title="EduBuilder EX2",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        * {
            font-family: 'Inter', sans-serif !important;
            direction: ltr !important;
        }

        @keyframes gradient_wave {
            0% { background-position: 0% 50%; }
            25% { background-position: 50% 100%; }
            50% { background-position: 100% 50%; }
            75% { background-position: 50% 0%; }
            100% { background-position: 0% 50%; }
        }

        .stApp {
            background: linear-gradient(-45deg, #0b1f3a, #123f6b, #1f78c1, #f57c00, #ff9f1c, #0b1f3a);
            background-size: 500% 500%;
            animation: gradient_wave 16s ease-in-out infinite;
            min-height: 100vh;
        }

        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
        }

        [data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid #e5e7eb !important;
        }

        [data-testid="stSidebarContent"] {
            background: #ffffff !important;
        }

        [data-testid="collapsedControl"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #111111 !important;
        }

        [data-testid="stSidebar"] .stRadio > label {
            display: none !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 0.8rem !important;
            padding-top: 0.5rem !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
            padding: 0.85rem 1rem !important;
            border-radius: 12px !important;
            border: 2px solid transparent !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {
            font-weight: 700 !important;
            margin: 0 !important;
            color: white !important;
            font-size: 1.05rem !important;
            text-align: center !important;
            width: 100% !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(1) {
            background: linear-gradient(135deg, #1f78c1 0%, #3ca0f0 100%) !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(2) {
            background: linear-gradient(135deg, #f57c00 0%, #ff9f1c 100%) !important;
        }

        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked) {
            border: 2px solid #ffffff !important;
            box-shadow: 0 0 0 3px #111111, 0 8px 16px rgba(0,0,0,0.2) !important;
            transform: scale(1.03) !important;
            filter: brightness(1.12) !important;
        }

        [data-testid="stChatMessage"] {
            background-color: white !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
            border: 1px solid #edf2f7 !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background-color: #f0f4ff !important;
            border-color: #e2e8f0 !important;
        }

        [data-testid="stBottomBlockContainer"] {
            background: #ffffff !important;
            border-top: 1px solid #e5e7eb !important;
            padding-top: 0.35rem !important;
        }

        [data-testid="stBottomBlockContainer"] > div,
        [data-testid="stChatInputContainer"] {
            background: #ffffff !important;
        }

        [data-testid="stChatInput"] {
            background: #ffffff !important;
            border: 2px solid #f57c00 !important;
            border-radius: 14px !important;
            box-shadow: 0 6px 18px rgba(245, 124, 0, 0.16) !important;
        }

        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input {
            background: #ffffff !important;
            color: #111111 !important;
        }

        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder {
            color: #9a3412 !important;
            opacity: 0.95 !important;
        }

        .stDownloadButton > button,
        .stButton > button {
            background: linear-gradient(135deg, #5b7cfa 0%, #8b5fbf 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.65rem 1rem !important;
            font-weight: 700 !important;
            width: 100% !important;
        }

        .metric-card {
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 10px 24px rgba(0,0,0,0.1);
        }

        .metric-title {
            color: rgba(255,255,255,0.82) !important;
            font-size: 0.9rem;
        }

        .metric-value {
            color: white !important;
            font-size: 1.75rem;
            font-weight: 800;
        }

        .catalog-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 18px rgba(0,0,0,0.12);
            margin-bottom: 1rem;
        }

        .catalog-body {
            padding: 1rem 1.15rem 1.15rem 1.15rem;
            color: #111827 !important;
        }

        .catalog-body p,
        .catalog-body strong {
            color: #111827 !important;
        }

        .hint-box {
            background: rgba(255,255,255,0.9);
            color: #111827 !important;
            border-radius: 14px;
            padding: 0.85rem 1rem;
            border-left: 4px solid #f57c00;
            margin-bottom: 1rem;
        }

        h1, h2, h3 {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "ex2_messages" not in st.session_state:
        st.session_state.ex2_messages = [
            {
                "role": "assistant",
                "content": (
                    "Describe the course you want to build, and I will save it as a learning plan.\n\n"
                    "Example: `Create a beginner Python loops course for first-year students.`"
                ),
            }
        ]
    if "ex2_created_ids" not in st.session_state:
        st.session_state.ex2_created_ids = []
    if "ex2_page" not in st.session_state:
        st.session_state.ex2_page = "Create Course"


def fetch_plans() -> list[dict]:
    response = requests.get(f"{API_URL}/plans", timeout=10)
    response.raise_for_status()
    return response.json()


def infer_level(prompt: str) -> str:
    lowered = prompt.lower()
    for keyword, level in LEVEL_KEYWORDS.items():
        if keyword in lowered:
            return level
    return "Beginner"


def infer_title(prompt: str) -> str:
    clean = re.sub(r"^(create|build|make)\s+", "", prompt.strip(), flags=re.IGNORECASE)
    clean = clean.rstrip(".!?")
    return (clean or "New Learning Plan")[:120].title()


def infer_goal(prompt: str) -> str:
    prompt = prompt.strip()
    return prompt if len(prompt) <= 240 else prompt[:237] + "..."


def infer_cues(prompt: str) -> str:
    lowered = prompt.lower()
    cues = []
    if "beginner" in lowered or "intro" in lowered:
        cues.append("Start with one gentle concept and one worked example in every lesson.")
    if "project" in lowered or "practice" in lowered:
        cues.append("Close each lesson with a short practice task.")
    if "exam" in lowered or "test" in lowered:
        cues.append("End each section with a quick recap question.")
    if not cues:
        cues.append("Keep the plan practical, short, and easy to review.")
    return " ".join(cues)[:300]


def build_plan_payload(prompt: str) -> dict:
    return {
        "title": infer_title(prompt),
        "goal": infer_goal(prompt),
        "cues": infer_cues(prompt),
        "level": infer_level(prompt),
        "is_public": True,
    }


def create_plan_from_prompt(prompt: str) -> dict:
    response = requests.post(f"{API_URL}/plans", json=build_plan_payload(prompt), timeout=10)
    response.raise_for_status()
    return response.json()


def plans_to_csv(plans: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "title", "goal", "cues", "level", "is_public", "created_at"],
    )
    writer.writeheader()
    for plan in plans:
        writer.writerow({key: plan.get(key, "") for key in writer.fieldnames})
    return output.getvalue()


def render_metrics(plans: list[dict]) -> None:
    public_count = sum(1 for plan in plans if plan.get("is_public"))
    my_session_count = sum(1 for plan in plans if plan.get("id") in st.session_state.ex2_created_ids)
    latest_created = max((plan.get("created_at", "") for plan in plans), default="")
    latest_label = latest_created[:10] if latest_created else "No entries yet"

    cols = st.columns(3)
    metric_data = [
        ("Plans in catalog", str(len(plans))),
        ("Created this session", str(my_session_count)),
        ("Public plans | latest", f"{public_count} | {latest_label}"),
    ]
    for col, (title, value) in zip(cols, metric_data):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_create_course_page() -> None:
    st.title("Create Course")
    st.markdown(
        "This EX2 screen keeps the chat-style creation flow, but it only talks to the EX1 `/plans` API."
    )
    st.markdown(
        """
        <div class="hint-box">
        No login, no auth prompts, and no extra backend endpoints. Type a course idea and it will be saved immediately.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for message in st.session_state.ex2_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("you can type here")
    if not prompt:
        return

    st.session_state.ex2_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Saving your course idea..."):
            try:
                created = create_plan_from_prompt(prompt)
            except requests.RequestException as exc:
                reply = (
                    "I could not reach the EX1 backend. Start `poseai_backend.main_ex1:app` first, "
                    "then try again.\n\n"
                    f"Technical detail: `{exc}`"
                )
                st.markdown(reply)
                st.session_state.ex2_messages.append({"role": "assistant", "content": reply})
                return

            st.session_state.ex2_created_ids.append(created["id"])
            reply = (
                f"Saved **{created['title']}** as a new plan.\n\n"
                f"- Goal: {created['goal']}\n"
                f"- Level: {created['level']}\n"
                f"- Public: {'Yes' if created['is_public'] else 'No'}\n\n"
                "Open `Course Catalog` in the sidebar to see it immediately."
            )
            st.markdown(reply)
            st.session_state.ex2_messages.append({"role": "assistant", "content": reply})


def render_catalog_page(plans: list[dict]) -> None:
    st.title("Course Catalog")
    st.markdown("Browse all public learning plans returned by the EX1 backend.")
    render_metrics(plans)
    st.markdown("")
    st.download_button(
        label="Export catalog to CSV",
        data=plans_to_csv(plans),
        file_name="edubuilder-ex2-catalog.csv",
        mime="text/csv",
    )
    st.markdown("")

    if not plans:
        st.info("No plans yet. Create the first one from the chat page.")
        return

    for index, plan in enumerate(plans):
        gradient = CARD_COLORS[index % len(CARD_COLORS)]
        created_label = plan.get("created_at", "")
        if created_label:
            try:
                created_label = datetime.fromisoformat(created_label).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                created_label = str(created_label)

        session_badge = ""
        if plan.get("id") in st.session_state.ex2_created_ids:
            session_badge = (
                "<div style='margin-top:0.75rem;padding:0.55rem 0.8rem;background:#fff7ed;"
                "border-left:4px solid #f57c00;border-radius:8px;color:#9a3412;font-weight:700;'>"
                "Created in this session</div>"
            )

        st.markdown(
            f"""
            <div class="catalog-card">
                <div style="background:{gradient};padding:0.95rem 1.1rem;color:white;font-weight:800;font-size:1.02rem;">
                    {plan.get("title", "Untitled plan")}
                </div>
                <div class="catalog-body">
                    <p><strong>Goal:</strong> {plan.get("goal", "")}</p>
                    <p><strong>Cues:</strong> {plan.get("cues", "")}</p>
                    <p><strong>Level:</strong> {plan.get("level", "")}</p>
                    <p><strong>Created:</strong> {created_label}</p>
                    {session_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    apply_custom_css()
    init_state()

    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Create Course", "Course Catalog"],
        key="ex2_page",
        label_visibility="collapsed",
    )

    try:
        plans = fetch_plans()
    except requests.RequestException as exc:
        st.title("EduBuilder EX2")
        st.error(
            "Could not connect to the EX1 backend. Run `uv run uvicorn poseai_backend.main_ex1:app --reload` "
            "and refresh this page."
        )
        st.code(str(exc))
        return

    if page == "Create Course":
        render_create_course_page()
    else:
        render_catalog_page(plans)


if __name__ == "__main__":
    main()
