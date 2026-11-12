import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone

import av
import cv2
import pandas as pd
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

APP_TITLE = "Face Detection | Phase I"
DB_PATH = os.getenv("ANALYTICS_DB_PATH", "visitor_analytics.db")
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

st.set_page_config(page_title=APP_TITLE, page_icon="👁️", layout="wide")

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def get_db():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            session_id TEXT PRIMARY KEY,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            page TEXT NOT NULL,
            user_agent TEXT,
            browser TEXT,
            device TEXT,
            consent_to_analytics INTEGER NOT NULL DEFAULT 1,
            name TEXT,
            email TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            page TEXT NOT NULL,
            viewed_at TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection

def parse_browser(user_agent):
    ua = user_agent or ""
    if "Edg/" in ua:
        browser = "Microsoft Edge"
    elif "Chrome/" in ua and "Chromium" not in ua:
        browser = "Google Chrome"
    elif "Firefox/" in ua:
        browser = "Mozilla Firefox"
    elif "Safari/" in ua and "Chrome/" not in ua:
        browser = "Safari"
    else:
        browser = "Other / unavailable"
    if "Android" in ua or "iPhone" in ua or "Mobile" in ua:
        device = "Mobile"
    elif "iPad" in ua or "Tablet" in ua:
        device = "Tablet"
    elif ua:
        device = "Desktop"
    else:
        device = "Unavailable"
    return browser, device

def supabase_settings():
    try:
        return st.secrets.get("supabase", {})
    except Exception:
        return {}

def save_visit(session_id, page, user_agent, browser, device):
    cfg = supabase_settings()
    url = cfg.get("url", "").rstrip("/")
    key = cfg.get("service_role_key", "")
    record = {
        "session_id": session_id,
        "first_seen": utc_now(),
        "last_seen": utc_now(),
        "page": page,
        "user_agent": user_agent[:500],
        "browser": browser,
        "device": device,
        "consent_to_analytics": True,
    }
    if url and key:
        import requests
        endpoint = url + "/rest/v1/visitors?on_conflict=session_id"
        response = requests.post(
            endpoint,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            json=record,
            timeout=10,
        )
        response.raise_for_status()
        return "Supabase"
    with get_db() as conn:
        conn.execute("""
            INSERT INTO visitors
                (session_id, first_seen, last_seen, page, user_agent, browser, device, consent_to_analytics)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(session_id) DO UPDATE SET
                last_seen=excluded.last_seen,
                page=excluded.page,
                user_agent=excluded.user_agent,
                browser=excluded.browser,
                device=excluded.device
        """, (session_id, record["first_seen"], record["last_seen"], page,
              record["user_agent"], browser, device))
        conn.commit()
    return "Local SQLite (temporary on most cloud hosts)"

def save_page_view(session_id, page):
    cfg = supabase_settings()
    url = cfg.get("url", "").rstrip("/")
    key = cfg.get("service_role_key", "")
    event = {"session_id": session_id, "page": page, "viewed_at": utc_now()}
    if url and key:
        import requests
        response = requests.post(
            url + "/rest/v1/page_views",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json=event,
            timeout=10,
        )
        response.raise_for_status()
    else:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO page_views(session_id, page, viewed_at) VALUES (?, ?, ?)",
                (session_id, page, event["viewed_at"]),
            )
            conn.commit()

def load_analytics():
    cfg = supabase_settings()
    url = cfg.get("url", "").rstrip("/")
    key = cfg.get("service_role_key", "")
    if url and key:
        import requests
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        visitors = requests.get(
            url + "/rest/v1/visitors?select=*&order=last_seen.desc&limit=1000",
            headers=headers, timeout=10
        )
        visitors.raise_for_status()
        views = requests.get(
            url + "/rest/v1/page_views?select=*&order=viewed_at.desc&limit=2000",
            headers=headers, timeout=10
        )
        views.raise_for_status()
        return pd.DataFrame(visitors.json()), pd.DataFrame(views.json()), "Supabase"
    with get_db() as conn:
        visitors = pd.read_sql_query("SELECT * FROM visitors ORDER BY last_seen DESC", conn)
        views = pd.read_sql_query("SELECT * FROM page_views ORDER BY viewed_at DESC", conn)
    return visitors, views, "Local SQLite"

class FaceDetector(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.CascadeClassifier(CASCADE_PATH)

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (40, 210, 120), 2)
        cv2.putText(image, f"Faces detected: {len(faces)}", (16, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 210, 120), 2)
        return av.VideoFrame.from_ndarray(image, format="bgr24")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.hero {padding: 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#101d36,#173c50); color: white;}
.small-muted {color: #8a94a6; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Phase I Demo")
page = st.sidebar.radio("Navigate", ["Home", "Live face detection", "Visitor registration", "Admin analytics"])
st.sidebar.caption("Face detection only • OpenCV Haar Cascade")

# Anonymous analytics notice: this tracks a random session ID and basic browser/device class.
# It does not record camera frames, face images, names, email addresses, or IP addresses.
st.sidebar.info("Anonymous usage analytics are active when this notice is displayed. No camera image is recorded by analytics.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "analytics_page" not in st.session_state:
    st.session_state.analytics_page = None

try:
    from streamlit_javascript import st_javascript
    user_agent = st_javascript("navigator.userAgent", key="browser_user_agent") or ""
except Exception:
    user_agent = ""

browser, device = parse_browser(user_agent)
if st.session_state.analytics_page != page:
    try:
        st.session_state.analytics_storage = save_visit(
            st.session_state.session_id, page, user_agent, browser, device
        )
        save_page_view(st.session_state.session_id, page)
        st.session_state.analytics_page = page
    except Exception as exc:
        st.session_state.analytics_error = str(exc)

if page == "Home":
    st.markdown('<div class="hero"><h1>Real-Time Face Detection</h1><p>Phase I showcase • Detect faces in a live camera stream using OpenCV.</p></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Project overview")
        st.write("This project detects the number and position of faces in a live video stream. It does not identify people or recognize identities.")
        st.write("- Haar Cascade frontal-face detector")
        st.write("- Live browser camera stream")
        st.write("- Face bounding boxes and live count")
        st.write("- Anonymous visitor analytics with a privacy notice")
        st.info("Your camera starts only when you open Live face detection and press START. The analytics system does not access or save camera frames.")
    with right:
        st.subheader("Technology")
        st.metric("Detection model", "Haar Cascade")
        st.metric("Project phase", "Phase I")
        st.metric("Purpose", "Detection only")
    st.button("Open live demo", on_click=lambda: st.session_state.update({"go_demo": True}))
    if st.session_state.get("go_demo"):
        st.info("Choose **Live face detection** in the sidebar to start the camera.")

elif page == "Live face detection":
    st.title("Live face detection")
    st.write("The browser will ask for camera permission when you press START. The camera stream is processed for live detection; frames are not stored.")
    st.warning("Camera access is optional. Stop the stream at any time using STOP.")
    webrtc_streamer(
        key="phase1-face-detection",
        video_processor_factory=FaceDetector,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    st.caption("Detection runs while the stream is active. No identity recognition is performed.")

elif page == "Visitor registration":
    st.title("Register your interest (optional)")
    st.write("You can explore the face-detection demo without registering. If you want us to contact you about the project, submit this form.")
    with st.form("visitor_registration"):
        name = st.text_input("Name (optional)")
        email = st.text_input("Email (optional)")
        contact_ok = st.checkbox("I agree that my submitted details may be used to contact me about this project.")
        submitted = st.form_submit_button("Submit registration")
    if submitted:
        if not contact_ok:
            st.error("Please tick the contact permission box, or leave the form without submitting.")
        elif not (name.strip() or email.strip()):
            st.error("Enter a name or email address.")
        else:
            cfg = supabase_settings()
            url = cfg.get("url", "").rstrip("/")
            key = cfg.get("service_role_key", "")
            try:
                if url and key:
                    import requests
                    response = requests.patch(
                        url + "/rest/v1/visitors?session_id=eq." + st.session_state.session_id,
                        headers={"apikey": key, "Authorization": f"Bearer {key}",
                                 "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={"name": name.strip() or None, "email": email.strip() or None},
                        timeout=10,
                    )
                    response.raise_for_status()
                else:
                    with get_db() as conn:
                        conn.execute("UPDATE visitors SET name=?, email=? WHERE session_id=?",
                                     (name.strip() or None, email.strip() or None, st.session_state.session_id))
                        conn.commit()
                st.success("Registration saved. Thank you.")
            except Exception as exc:
                st.error(f"Could not save registration: {exc}")

elif page == "Admin analytics":
    st.title("Private visitor analytics")
    try:
        admin_password = st.secrets.get("admin", {}).get("password", "")
    except Exception:
        admin_password = ""
    if not admin_password:
        st.error("Admin dashboard is locked until ADMIN_PASSWORD is configured in the hosting secrets.")
        st.code('admin = { password = "replace-with-a-long-random-password" }', language="toml")
    else:
        entered = st.text_input("Admin password", type="password")
        if entered and entered == admin_password:
            try:
                visitors, views, storage = load_analytics()
                st.caption(f"Data source: {storage}")
                total = len(visitors)
                registered = int(visitors["email"].notna().sum()) if total and "email" in visitors else 0
                a, b, c = st.columns(3)
                a.metric("Tracked sessions", total)
                b.metric("Registered contacts", registered)
                c.metric("Page views", len(views))
                if total:
                    st.subheader("Recent visitor sessions")
                    visible = [c for c in ["first_seen", "last_seen", "page", "browser", "device", "name", "email"] if c in visitors.columns]
                    st.dataframe(visitors[visible], use_container_width=True, hide_index=True)
                    if "browser" in visitors:
                        st.subheader("Browser breakdown")
                        st.bar_chart(visitors["browser"].fillna("Unavailable").value_counts())
                if len(views):
                    st.subheader("Recent page views")
                    st.dataframe(views[["viewed_at", "page", "session_id"]].head(100),
                                 use_container_width=True, hide_index=True)
                st.caption("Visitor sessions are not verified real-world identities. IP addresses and precise location are not collected by this app.")
            except Exception as exc:
                st.error(f"Analytics could not be loaded: {exc}")
        elif entered:
            st.error("Incorrect password.")

st.divider()
st.caption("Privacy: anonymous session analytics use a random session ID and basic browser/device information. No IP address, precise location, camera frame, or face image is collected or stored by analytics. Contact details are saved only after the visitor submits the optional form and checks the permission box.")
