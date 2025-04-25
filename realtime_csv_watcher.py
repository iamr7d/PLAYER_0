import os
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CSV_PATH = os.path.join("csv", "realtime", "realtime_log.csv")  # Change this to your real-time CSV filename
MOVIE_NAME = "Your Movie Name"  # Optionally set dynamically
TABLE_NAME = "viewer_logs"  # Update if your table name is different

last_line = 0

def get_new_rows():
    global last_line
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        new_rows = reader[last_line:]
        last_line = len(reader)
        return new_rows

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            new_rows = get_new_rows()
            for row in new_rows:
                data = {
                    "blink_count": int(row["blink_count"]),
                    "elapsed_time": row["elapsed_time"],
                    "real_time": row["real_time"],
                    "movie_name": MOVIE_NAME
                }
                try:
                    from firebase_upload import upload_viewer_log
                    upload_viewer_log(data["blink_count"], data["elapsed_time"], data["real_time"], data["movie_name"])
                except Exception as e:
                    print("Error:", e)

if __name__ == "__main__":
    # Initialize last_line to skip existing rows
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            last_line = sum(1 for _ in f) - 1  # -1 for header
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(CSV_PATH), recursive=False)
    observer.start()
    print(f"Watching {CSV_PATH} for real-time updates...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
