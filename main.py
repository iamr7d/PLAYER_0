from PyQt6.QtWidgets import QApplication
import sys
from player_window import ModernVideoPlayer

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = ModernVideoPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
