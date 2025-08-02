# ✅ Full Data Detox App with Pale Red Background

import streamlit as st
import pandas as pd
import drive_scan
import gmail_scan
import json
import os
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow

# 🌐 OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.readonly'
]

st.set_page_config(page_title="Data Detox", layout="wide", page_icon="🧼")

# 🎨 Pale Red Background Theme
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #fae5e5;
            color: #333;
        }
        .stButton > button {
            background-color: #e50914;
            color: white;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px 30px;
            margin: 10px 0;
        }
        .stTabs [role="tab"] {
            background-color: #1f1f1f;
            border: 1px solid #444;
            border-radius: 6px;
            margin-right: 8px;
            padding: 10px;
            font-weight: 600;
            color: #f2f2f2;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e50914 !important;
            color: white !important;
        }
        .stMetricValue {
            font-size: 28px;
        }
        .stMetricLabel {
            font-size: 18px;
        }
        .stDataFrame, .stTable {
            background-color: #fff;
            color: #000;
        }
        .st-expanderHeader {
            background-color: #ffe5e5;
            font-weight: bold;
            font-size: 18px;
            color: #111;
        }
        h1, h2, h3, h4, h5 {
            color: #e50914 !important;
        }
        .element-container, .block-container {
            color: #222 !important;
        }
        .stMarkdown, .stText, .stCaption, .stInfo, .stSuccess, .stError {
            color: #222 !important;
        }
        /* Section-specific coloring */
        .large-files .st-expanderHeader { background-color: #ffcccc !important; color: #660000; }
        .old-files .st-expanderHeader { background-color: #ffd6d6 !important; color: #800000; }
        .public-files .st-expanderHeader { background-color: #ffe5e5 !important; color: #990000; }
    </style>
""", unsafe_allow_html=True)

st.title("\U0001f9fc Data Detox Dashboard")

# 🛡️ Auth setup
def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_833291583235-fs74ee721n13aiglbrksj2f6rof2m217.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds

# ⛓ History saver
def save_history(data, filename):
    history_dir = "history"
    os.makedirs(history_dir, exist_ok=True)
    path = os.path.join(history_dir, filename)
    with open(path, "w") as f:
        json.dump(data, f)

# 🔐 Login
if "creds" not in st.session_state:
    if st.button("🔐 Connect with Google"):
        st.session_state.creds = authenticate()

# 📂 After login
if "creds" in st.session_state:
    creds = st.session_state.creds
    drive_service = drive_scan.get_drive_service(creds)
    gmail_service = gmail_scan.get_gmail_service(creds)

    with st.spinner("🔍 Scanning your Drive and Gmail..."):
        files = drive_scan.list_files(drive_service)
        old_files, large_files, public_files = drive_scan.classify_files(files)
        emails = gmail_scan.scan_old_emails(gmail_service)

    # ⬇️ Save scan history
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_history({"files": files, "emails": emails}, f"scan_{now}.json")

    # ✅ Summary
    st.success(f"Total files: {len(files)} | Total emails scanned: {len(emails)}")

    # 🔢 Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Large Files", len(large_files))
    col2.metric("Old Files", len(old_files))
    col3.metric("Public Files", len(public_files))
    col4.metric("Old Emails", len(emails))

    # 🔹 Tabs
    tabs = st.tabs(["📂 All Files", "📜 Old Files", "📀 Large Files", "🔓 Public Files", "📧 Gmail Report"])

    def show_files(tab, file_list, label, css_class=""):
        with tab:
            if not file_list:
                st.success(f"No {label.lower()} found 🎉")
            else:
                for file in file_list:
                    with st.container():
                        with st.expander(f"📄 {file['name']}"):
                            st.markdown(f"**Size:** {round(int(file.get('size', 0)) / (1024*1024), 2)} MB")
                            st.markdown(f"**Modified:** {file.get('modifiedTime', 'N/A')}")
                            st.markdown(f"[Open]({file.get('webViewLink')})")

                            if st.button(f"🗑️ Delete", key=f"{file['id']}_{label}"):
                                result = drive_scan.delete_file(drive_service, file['id'])
                                if result:
                                    st.success("Deleted")
                                else:
                                    st.error("Failed")

    show_files(tabs[0], files, "All")
    show_files(tabs[1], old_files, "Old", "old-files")
    show_files(tabs[2], large_files, "Large", "large-files")
    show_files(tabs[3], public_files, "Public", "public-files")

    with tabs[4]:
        if emails:
            df = pd.DataFrame(emails)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Export Emails", csv, "old_emails.csv", "text/csv")
        else:
            st.success("No old emails found 🎉")

    st.markdown("---")
    st.markdown("Made by Prem Sagar • GitHub: [premxyz](https://github.com/premxyz)")
