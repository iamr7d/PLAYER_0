from PyQt6.QtWidgets import QApplication
import sys
from player_window import ModernVideoPlayer
from firebase_upload import upload_pending_logs

def main():
    # Try to upload any pending logs from offline sessions
    try:
        upload_pending_logs()
    except Exception as e:
        print(f"[WARNING] Could not upload pending logs: {e}")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = ModernVideoPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
