# Face Detection – Phase I

A real-time face detection showcase built with Python, OpenCV Haar Cascade, and Streamlit.

## Features

- Original desktop webcam script: `faceid.py`
- Browser-based live face detection: `app.py`
- Visitor analytics: random session ID, timestamps, page views, browser and device class
- Optional visitor registration with an explicit contact-permission checkbox
- Password-protected admin analytics page
- No identity recognition and no automatic camera-image storage

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit. On the Live face detection page, press START and grant camera permission in the browser.

## Visitor analytics storage

Without Supabase credentials, analytics are stored in a local SQLite file named `visitor_analytics.db`. This is suitable for local testing only. Many hosted app filesystems are temporary, so use Supabase for persistent hosted analytics.

1. Create a Supabase project.
2. Open the SQL Editor and run `supabase_schema.sql`.
3. In your hosting provider's Streamlit secrets, add the values from `.streamlit/secrets.toml.example`.
4. Set a strong, unique admin password.
5. Redeploy the app.

Never commit the real Supabase service-role key or admin password. The service-role key must remain server-side.

## Privacy and limits

The app displays an analytics notice and tracks a random session ID, timestamps, page views, browser family, and device class. It does not collect IP addresses or precise location. A Streamlit deployment may not expose reliable visitor IP information to the Python app, so this implementation deliberately does not guess or infer it.

Name and email are optional. They are stored only after a visitor submits the registration form and checks the contact-permission box. Camera permission is requested only when the visitor starts the live demo. Live camera frames are processed for detection and are not saved by this app.

This app does not automatically save face images to Google Drive. That requires a separate, explicit capture-and-save action, a disclosed purpose, a configured private Drive folder, and server-side credentials.

## Existing desktop test

Run the original desktop detector with `python faceid.py`. Run the image-based checks with `python test_face_detection.py` after placing the expected sample images in the local `test_images/` folder.
