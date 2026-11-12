# Face Detection – Phase I

A Python-based real-time face-detection project with a desktop webcam program and a browser-hosted Streamlit showcase.

**Live demo:** https://hhggpqgfksdbcqgx4soabe.streamlit.app/  
**GitHub:** https://github.com/sridharanpalanisamy/Face-recognition-Phase-I-

> **Scope:** Phase I detects face-like regions and draws bounding boxes. It does **not** identify a person, compare faces against a database, verify identity, or perform facial recognition.

## 1. Project features

- Desktop webcam detection using `faceid.py`.
- Browser webcam detection using `app.py` and Streamlit WebRTC.
- OpenCV Haar Cascade frontal-face detector.
- Grayscale preprocessing, face bounding boxes, and live face count.
- Streamlit pages: Home, Live face detection, Visitor registration, and Admin analytics.
- Random session identifiers, page-view timestamps, browser family, and device category.
- Optional visitor name/email registration, saved only after form submission and contact permission.
- Password-protected admin analytics.
- Supabase REST API storage when configured; local SQLite fallback otherwise.
- IP address recording when Streamlit exposes the connection IP, with a visible privacy notice and session opt-out.

## 2. Technology and why it is used

| Technology | Role in this project | Why it is used |
|---|---|---|
| Python | Main programming language | Readable and has mature computer-vision libraries |
| OpenCV | Image processing and face detection | Provides Haar Cascade model loading, grayscale conversion, detection, and drawing |
| Haar Cascade XML | Pre-trained frontal-face detector | Lightweight baseline suitable for a Phase I demonstration |
| Streamlit | Browser-based user interface | Builds the demo and admin pages in Python |
| streamlit-webrtc | Browser camera/video transport | Sends live camera frames to the Streamlit video processor |
| PyAV (`av`) | Video frame conversion | Converts frames between WebRTC and OpenCV-compatible arrays |
| pandas | Analytics tables | Displays visitor and page-view records |
| SQLite | Local fallback database | Enables local testing without a hosted database |
| Supabase / PostgreSQL | Hosted analytics database | Persists visitor and page-view records across hosted app restarts |
| Streamlit Community Cloud | Hosting | Publishes the Python app from the GitHub repository |
| GitHub | Source control and deployment source | Stores code and provides a versioned deployment workflow |

## 3. Repository files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application, live detector, registration, analytics, and Supabase/SQLite access |
| `faceid.py` | Standalone desktop webcam detector |
| `test_face_detection.py` | Image-based test runner for expected face counts |
| `requirements.txt` | Python package dependencies |
| `supabase_schema.sql` | Database tables and security setup |
| `.streamlit/secrets.toml.example` | Template for local/hosted secret configuration; contains placeholders only |
| `README.md` | Project setup and operating instructions |

## 4. Requirements

- Windows, macOS, or Linux computer for local development.
- Python 3.10 or newer recommended.
- Working webcam for live detection.
- Modern browser with camera permission for the hosted demo.
- Internet connection for Streamlit Cloud and Supabase.
- Supabase project for persistent hosted analytics (optional for local-only testing).

Use a well-lit environment. Face the camera, keep the face visible, and avoid strong backlighting or extreme angles.

## 5. Run locally

Open a terminal in the repository folder.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks environment activation, use Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit (usually `http://localhost:8501`).

### Run the desktop webcam version

```bash
python faceid.py
```

The desktop window displays detected faces and a count. Press **E** to exit. The program releases the webcam and closes its OpenCV window when it exits.

## 6. How to use the hosted website

1. Open the live demo URL.
2. Read the privacy notice in the sidebar.
3. Choose **Home** to read the project overview.
4. Choose **Live face detection** to open the camera panel.
5. Press **START** in the video component.
6. When the browser asks for camera permission, allow access only if you want to test the detector.
7. Position your face in view. A rectangle should appear around each detected face and the count should update.
8. Press **STOP** when finished.
9. Use **Visitor registration** only if you want to submit contact details. Registration is optional.
10. Admins can choose **Admin analytics**, enter the configured admin password, and inspect the records.

Camera permission is controlled by the browser. If permission was denied earlier, change the camera permission for the site in the browser's site settings and reload.

## 7. How face detection works

1. OpenCV loads `haarcascade_frontalface_default.xml` from its installed data directory.
2. The webcam or browser video processor receives a frame.
3. The frame is converted from BGR colour to grayscale.
4. `detectMultiScale` scans the grayscale image for patterns matching frontal faces.
5. For each detected region, the program receives coordinates `(x, y, w, h)`.
6. A rectangle is drawn around each region.
7. The number of detected regions is displayed.

Current detector parameters in the code:

- `scaleFactor=1.3`: image pyramid scaling between detection passes.
- `minNeighbors=5`: minimum neighbour support used to reduce weak detections.

These values are starting parameters, not a guarantee of perfect detection. Lighting, pose, distance, camera quality, occlusion, and image resolution affect results.

## 8. Visitor analytics and data storage

### Data collected by the current app

- Random session ID (not a verified real-world identity).
- First-seen and last-seen timestamps.
- Current page and page-view timestamps.
- Browser family and broad device category, when browser information is available.
- Connection IP address when exposed by Streamlit, unless the visitor opts out for the session.
- Name/email only when the visitor submits the optional registration form and checks the contact-permission box.

The app does not perform identity recognition, does not automatically capture or store face images, and does not collect camera frames for analytics. It does not derive a person's exact physical address from an IP address.

### IP address behavior and limitation

The sidebar explains IP analytics and offers an opt-out checkbox. By default, the app attempts to read `st.context.ip_address`; if the visitor opts out, it writes a null IP for that session. The value is validated as an IP address before storage.

The hosting platform or network proxy may not expose the visitor's original IP to the app. In that case the database value remains blank. The application intentionally does not trust arbitrary browser-supplied forwarding headers or invent an address. A blank IP does not necessarily mean no visitor arrived.

### Local SQLite vs Supabase

- If Supabase URL and server-side key are configured, the app uses Supabase REST endpoints.
- Otherwise, it uses `visitor_analytics.db` in local SQLite.
- Local SQLite is useful for development. Hosted filesystems may be temporary; do not rely on it for durable cloud analytics.

## 9. Supabase setup

1. Create a Supabase project.
2. Open **SQL Editor** in the Supabase dashboard.
3. Open this repository's `supabase_schema.sql`, copy its SQL, and run it.
4. Confirm the `visitors` and `page_views` tables exist.
5. Keep the Supabase secret/service-role key on the server only.

For an existing project created before IP tracking, run this migration once:

```sql
ALTER TABLE public.visitors
ADD COLUMN IF NOT EXISTS ip_address TEXT;
```

The schema enables Row Level Security. The Streamlit server accesses the tables using the secret/service-role key. Never put that key in client-side code, public files, screenshots, or Git commits. The service-role key bypasses RLS, so protect it carefully and restrict who can access the hosting settings and admin dashboard.

## 10. Streamlit secrets configuration

In Streamlit Community Cloud:

1. Open the app's settings.
2. Open **Secrets**.
3. Add the configuration below using your own values.
4. Save and allow the app to restart.

```toml
[admin]
password = "REPLACE_WITH_A_LONG_UNIQUE_RANDOM_PASSWORD"

[supabase]
url = "https://YOUR_PROJECT_ID.supabase.co"
service_role_key = "YOUR_SUPABASE_SECRET_OR_SERVICE_ROLE_KEY"
```

Do not paste real keys into GitHub or share them in chat. If a secret has been exposed, rotate it in Supabase and update Streamlit secrets. Use a unique admin password; do not reuse an email or banking password.

## 11. Admin analytics

1. Select **Admin analytics** from the sidebar.
2. Enter the password configured under `[admin]`.
3. Check the **Data source** label. It should say Supabase if the URL and key are configured, otherwise Local SQLite.
4. Review tracked sessions, registered contacts, page views, and sessions with IP.
5. Inspect the recent visitor sessions table and the page-view table.

If analytics do not load:
- Confirm the app has restarted after saving secrets.
- Confirm Supabase project URL is exact and ends with `.supabase.co`.
- Confirm the secret key is current and is stored under the correct TOML key.
- Confirm the tables and `ip_address` column exist.
- Read the exact error displayed by the app.
- Never publish the secret key when asking for help.

If the IP column is blank:
- Confirm the visitor did not opt out.
- Confirm the deployed code is current.
- Confirm the Supabase `ip_address` column exists.
- Remember that Streamlit hosting may not expose the original client IP.

## 12. Testing

### Previously reported manual test

During the project development conversation, the user reported:
- Webcam: working.
- Face detection: 1 face detected.
- Error: None.

This is a user-reported manual test result, not an independently repeated test in this repository update.

### Image test runner

The script `test_face_detection.py` expects these files:

```text
test_images/
├── single_face.jpg
├── multiple_faces.jpg
└── no_face.jpg
```

Expected counts are 1, 2, and 0 respectively. Add suitable test images locally; do not commit photographs of people without permission. Run:

```bash
python test_face_detection.py
```

The script reports PASS, FAIL, NOT RUN, or ERROR. Missing images are reported as NOT RUN and cause the test run to exit unsuccessfully. The repository does not currently include those sample image files, so the image test suite is not automatically complete on a fresh clone.

### Manual test checklist

- [ ] Desktop webcam opens and exits with E.
- [ ] Browser camera starts only after pressing START and granting permission.
- [ ] One face produces a visible box and count.
- [ ] Two or more faces are detected in a suitable test scene.
- [ ] Empty scene reports zero faces.
- [ ] STOP ends the live camera stream.
- [ ] Visitor registration rejects submission without contact permission.
- [ ] Admin analytics rejects an incorrect password.
- [ ] Admin analytics loads from the intended data source.
- [ ] IP field is populated only when available and not opted out.
- [ ] Opt-out clears the session IP on the next app rerun.
- [ ] No camera frame or face image is written to analytics storage.

## 13. Troubleshooting

| Problem | Checks / solution |
|---|---|
| Webcam cannot open in desktop mode | Close other camera apps, check OS camera permission, try camera index 0, and reconnect the webcam |
| Browser camera does not start | Use HTTPS, allow camera permission, reload, and check that another app is not holding the camera |
| No face box appears | Improve lighting, face the camera, move closer, remove obstruction, and avoid extreme angles |
| Model could not load | Reinstall OpenCV and verify `cv2.data.haarcascades` exists |
| Missing Python module | Activate the correct virtual environment and run `pip install -r requirements.txt` |
| Supabase 404 on REST table | Confirm the table name/schema exists and reload the Supabase API schema after migrations |
| Supabase permission/401 error | Check the server-side secret key and table grants/policies; do not expose the key |
| Admin page says password not configured | Add the `[admin]` section in Streamlit Secrets and restart |
| Admin analytics empty | Check the data source label and verify the correct database is being queried |
| IP address blank | Platform may not expose the original client IP; check opt-out and database column; do not infer from untrusted headers |
| Local analytics disappear after redeploy | Use Supabase for persistence rather than temporary local storage |

## 14. Security, privacy, and operating constraints

- Give visitors a clear, visible privacy notice before or at the point analytics are collected.
- Provide an opt-out mechanism and honour it.
- Collect only data needed for the stated purpose.
- Define a retention period and delete records when no longer needed.
- Restrict the admin password and Supabase secret to trusted maintainers.
- Do not commit secrets, credentials, private visitor records, or personal photographs.
- Do not attempt to identify people from face boxes or IP addresses.
- Do not capture or store camera images without a separate, clear purpose and appropriate permission.
- Use the registration form only for voluntary contact details.
- Review applicable privacy and data-protection requirements before public production use. This README is technical guidance, not legal advice.

## 15. Current limitations and future scope

Current Phase I limitations:
- Haar Cascade is a traditional detector and can miss faces or produce false positives.
- Frontal-face detection is less reliable for profile views, masks, poor lighting, and occlusion.
- Detection is not identity recognition or biometric verification.
- IP availability depends on hosting/network behavior.
- The app has no built-in retention scheduler or visitor self-service data deletion workflow.
- Image tests require sample images that are not included in the repository.
- Admin authentication is a simple shared password; production use should use stronger access control and secret management.

Possible later improvements (not included in Phase I):
- Evaluate a modern face detector against a labelled test dataset.
- Add accuracy/latency measurements and a documented benchmark.
- Add a configurable data-retention process and admin deletion workflow.
- Add stronger administrator authentication and audit logging.
- Add a formal privacy page and deployment monitoring.

## 16. Project completion summary

Phase I delivers a working face-detection demonstration, desktop and web entry points, and a basic visitor analytics/admin workflow. The system detects faces in frames; it does not identify people. Use the manual checklist above before presenting a new deployment, and report only test results that have actually been observed.
