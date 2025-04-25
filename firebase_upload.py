import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import socket

# Path to your downloaded service account key
cred_path = os.path.join(os.path.dirname(__file__), '../filmda-aiplayer-firebase-adminsdk-fbsvc-72a30fa4a2.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

PENDING_DIR = os.path.join(os.path.dirname(__file__), 'pending_uploads')
os.makedirs(PENDING_DIR, exist_ok=True)

def is_connected():
    try:
        # Try to connect to a public DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except Exception:
        return False

def upload_pending_logs():
    """Upload all logs saved while offline."""
    for fname in os.listdir(PENDING_DIR):
        if fname.endswith('.json'):
            fpath = os.path.join(PENDING_DIR, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                _upload_to_firebase(data)
                os.remove(fpath)
            except Exception as e:
                print(f"Failed to upload pending log {fname}: {e}")

def _upload_to_firebase(data):
    collection_name = data["collection_name"]
    data_to_upload = data["data"]
    db.collection(collection_name).add(data_to_upload)
    print(f"Uploaded to Firebase [{collection_name}]:", data_to_upload)

def upload_viewer_log(blink_count, elapsed_time, real_time, movie_name, user_name=None):
    from datetime import datetime
    import re
    def clean_for_collection(name):
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        name = re.sub(r'_+', '_', name)
        return name.strip('_').lower()
    if not user_name:
        user_name = 'unknownuser'
    today = datetime.now().strftime('%Y%m%d')
    movie_clean = clean_for_collection(movie_name) if movie_name else 'unknownmovie'
    user_clean = clean_for_collection(user_name)
    collection_name = f"{user_clean}_{movie_clean}_{today}"
    data = {
        'blink_count': blink_count,
        'elapsed_time': elapsed_time,
        'real_time': real_time,
        'movie_name': movie_name,
        'user_name': user_name
    }
    payload = {
        "collection_name": collection_name,
        "data": data
    }
    if is_connected():
        # First upload any pending logs
        upload_pending_logs()
        # Then upload this log
        try:
            _upload_to_firebase(payload)
        except Exception as e:
            # If upload fails, save locally
            fname = f"offline_{collection_name}_{datetime.now().strftime('%H%M%S%f')}.json"
            fpath = os.path.join(PENDING_DIR, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            print(f"Failed to upload, saved offline: {fpath}")
    else:
        # Save log locally for later upload
        fname = f"offline_{collection_name}_{datetime.now().strftime('%H%M%S%f')}.json"
        fpath = os.path.join(PENDING_DIR, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
        print(f"No internet, saved offline: {fpath}")
