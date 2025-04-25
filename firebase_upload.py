import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your downloaded service account key
cred_path = os.path.join(os.path.dirname(__file__), '../filmda-aiplayer-firebase-adminsdk-fbsvc-72a30fa4a2.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

def upload_viewer_log(blink_count, elapsed_time, real_time, movie_name):
    data = {
        'blink_count': blink_count,
        'elapsed_time': elapsed_time,
        'real_time': real_time,
        'movie_name': movie_name
    }
    db.collection('viewer_logs').add(data)
    print("Uploaded to Firebase:", data)
