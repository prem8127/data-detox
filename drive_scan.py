# drive_scan.py
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def get_drive_service(credentials):
    return build('drive', 'v3', credentials=credentials)

def list_files(service, max_results=1000):
    results = service.files().list(
        pageSize=max_results,
        fields="nextPageToken, files(id, name, size, modifiedTime, shared, webViewLink)"
    ).execute()
    return results.get('files', [])

def classify_files(files):
    old_files = []
    large_files = []
    public_files = []

    for file in files:
        size = int(file.get("size", 0))
        modified_time = file.get("modifiedTime", "")
        shared = file.get("shared", False)

        if modified_time:
            try:
                dt = datetime.strptime(modified_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                if dt < datetime.now() - timedelta(days=365):
                    old_files.append(file)
            except:
                continue

        if size > 50 * 1024 * 1024:  # >50MB
            large_files.append(file)

        if shared:
            public_files.append(file)

    return old_files, large_files, public_files

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        return False
