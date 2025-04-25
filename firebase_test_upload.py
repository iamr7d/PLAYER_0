import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your downloaded service account key
cred_path = os.path.join(os.path.dirname(__file__), '../filmda-aiplayer-firebase-adminsdk-fbsvc-72a30fa4a2.json')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Example data
data = {
    'blink_count': 1,
    'elapsed_time': '0:00:01',
    'real_time': '2025-04-25 13:10:00',
    'movie_name': 'firebase_test'
}

# Add to 'viewer_logs' collection
db.collection('viewer_logs').add(data)
print("Uploaded to Firebase!")
