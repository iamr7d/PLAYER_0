import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your downloaded service account key
cred_path = os.path.join(os.path.dirname(__file__), '../filmda-aiplayer-firebase-adminsdk-fbsvc-72a30fa4a2.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

def upload_viewer_log(blink_count, elapsed_time, real_time, movie_name, user_name=None):
    from datetime import datetime
    import re
    def clean_for_collection(name):
        # Remove non-alphanum, replace spaces with _, lowercase
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
    db.collection(collection_name).add(data)
    print(f"Uploaded to Firebase [{collection_name}]:", data)
