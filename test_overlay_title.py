import os
import sys
import tempfile
from PyQt6.QtWidgets import QApplication
from overlay_title import OverlayTitleLabel

# Test filenames for extraction edge cases
test_filenames = [
    'Pravinkoodu.Shappu.2025.DS4K.1080p.SONYLIV.WEBRip.DD.mkv',
    'The.Godfather.Part.II.1974.1080p.BluRay.x264.YIFY.mp4',
    'Inception_2010_720p_WEB-DL.mkv',
    'Friends.S05E14.The.One.Where.Everybody.Finds.Out.720p.HDTV.x264.mkv',
    '12.Angry.Men.1957.1080p.BluRay.x265.HEVC.AAC-SARTRE.mkv',
    'Chernobyl.S01E05.Vichnaya.Pamyat.2019.1080p.WEBRip.HEVC.x265.mkv',
    'Movie.without.tags.mkv',
    'S01E01.mkv',
    'pr.mkv',
    'Avatar.2009.2160p.UHD.BluRay.x265.mkv',
    'Some.Movie.2022.mp4',
    'Old_Movie.1939.avi',
    'Show.Name.S2E3.720p.mkv',
    'Edge_Case_OnlyYear.2020.mkv',
    'Strange-File-Name-__.mkv',
]

def run_title_extraction_tests():
    app = QApplication(sys.argv)
    label = OverlayTitleLabel()
    print("\n--- Overlay Title Extraction Tests ---")
    for fname in test_filenames:
        label.show_title(fname, duration=100)
        # Extracted HTML text (for display)
        print(f"File: {fname}\n  Overlay: {label.text()}")
    print("--- End of Tests ---\n")
    app.quit()


def test_font_fallback():
    """
    Simulate missing Gotham font by renaming it if present, then restoring it.
    """
    font_path = os.path.join(os.path.dirname(__file__), 'gotham-regular.ttf')
    temp_path = None
    if os.path.exists(font_path):
        temp_path = font_path + '.bak'
        os.rename(font_path, temp_path)
    try:
        app = QApplication(sys.argv)
        label = OverlayTitleLabel()
        print("\n[Font Fallback Test] Font should fall back to Arial if Gotham is missing.")
        print(f"Font used: {label.font().family()}")
        app.quit()
    finally:
        if temp_path and os.path.exists(temp_path):
            os.rename(temp_path, font_path)

if __name__ == '__main__':
    run_title_extraction_tests()
    test_font_fallback()
