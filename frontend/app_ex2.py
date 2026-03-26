import io
import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="EduBuilder EX2", page_icon="📚", layout="wide")
st.title("📚 EduBuilder EX2 Demo")
st.caption("A lightweight Streamlit interface for listing courses and adding a new one without login prompts.")


def fetch_courses() -> list[dict]:
    try:
        response = requests.get(f"{API_URL}/courses", timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.error(f"Could not load courses: {exc}")
        return []


courses = fetch_courses()
df = pd.DataFrame(courses) if courses else pd.DataFrame(columns=["title", "content", "is_public", "created_at"])

left, right = st.columns([1, 2])

with left:
    st.subheader("Add a new course")
    with st.form("new_course_form", clear_on_submit=True):
        title = st.text_input("Course title")
        content = st.text_area("Course content", height=180)
        is_public = st.checkbox("Public course", value=True)
        submitted = st.form_submit_button("Save course", use_container_width=True)

    if submitted:
        if not title.strip() or not content.strip():
            st.warning("Please fill both title and content.")
        else:
            payload = {
                "title": title.strip(),
                "content": content.strip(),
                "is_public": is_public,
            }
            try:
                response = requests.post(f"{API_URL}/courses", json=payload, timeout=20)
                if response.status_code == 200:
                    st.success("Course saved successfully.")
                    st.rerun()
                else:
                    st.error(f"Save failed: {response.text}")
            except Exception as exc:
                st.error(f"Could not save course: {exc}")

    st.markdown("---")
    st.subheader("Small extra")
    st.metric("Visible courses", len(df.index))

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download catalog as CSV",
        data=csv_bytes,
        file_name="courses.csv",
        mime="text/csv",
        use_container_width=True,
    )

with right:
    st.subheader("Course catalog")
    if df.empty:
        st.info("No courses available yet.")
    else:
        display_df = df.copy()
        if "content" in display_df.columns:
            display_df["content"] = display_df["content"].astype(str).str.slice(0, 120)
        st.dataframe(display_df, use_container_width=True)

        st.markdown("### Quick view")
        for row in courses:
            with st.expander(row.get("title", "Untitled course")):
                st.write(row.get("content", ""))
