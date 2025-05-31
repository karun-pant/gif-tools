import sys
import threading
from PyQt5.QtWidgets import QApplication

from ui.main_window import FrameGifApp
from utils.styles import get_application_stylesheet

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    app.setStyleSheet(get_application_stylesheet())
    
    window = FrameGifApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()