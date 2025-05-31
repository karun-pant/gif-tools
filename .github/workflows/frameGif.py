import os
import sys
import time
import threading
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
                            QMessageBox, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PIL import Image, ImageDraw, ImageSequence
import io
import pkg_resources

# Color palette - Easy to customize
class AppColors:
    # Primary brand color (Cherry Red)
    PRIMARY = "#DE3163"
    # Darker shade of primary for hover effects
    PRIMARY_DARK = "#C42B56"
    # Lighter shade of primary for backgrounds
    PRIMARY_LIGHT = "#F5D6E0"
    # Secondary color for accents
    SECONDARY = "#4A90E2"
    # Text colors
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#FFFFFF"
    # Background colors
    BG_LIGHT = "#FFFFFF"
    BG_MEDIUM = "#F5F5F5"
    BG_DARK = "#E0E0E0"
    # Success, warning, error colors
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    ERROR = "#F44336"

def add_rounded_corners(im, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    im.putalpha(alpha)
    return im

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str, float)
    error = pyqtSignal(str)

class GifProcessor(threading.Thread):
    def __init__(self, gif_path, frame_path, output_path):
        super().__init__()
        self.gif_path = gif_path
        self.frame_path = frame_path
        self.output_path = output_path
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            start_time = time.time()
            
            # Resize GIF frames
            self.signals.status.emit("Resizing GIF frames...")
            gif_frames = self.resize_gif_frames(self.gif_path)
            
            # Overlay on frame
            self.signals.status.emit("Overlaying frames on background...")
            self.overlay_gif_on_frame(self.frame_path, gif_frames, self.output_path)
            
            elapsed_time = time.time() - start_time
            self.signals.finished.emit(self.output_path, elapsed_time)
            
        except Exception as e:
            self.signals.error.emit(str(e))
    
    def resize_gif_frames(self, input_gif):
        target_size = (2257, 4854)
        with Image.open(input_gif) as im:
            frames = []
            total_frames = im.n_frames
            
            for i, frame in enumerate(ImageSequence.Iterator(im), start=1):
                frame = frame.convert("RGBA")
                frame = frame.resize(target_size, Image.Resampling.LANCZOS)
                frames.append(frame)
                
                # Update progress (first half of the process)
                progress = int((i / total_frames) * 50)
                self.signals.progress.emit(progress)
        
        return frames
    
    def overlay_gif_on_frame(self, frame_path, gif_frames, output_path):
        radius = 275
        frame = Image.open(frame_path).convert("RGBA")
        frame_w, frame_h = frame.size

        processed_frames = []
        total_frames = len(gif_frames)
        
        for i, gif_frame in enumerate(gif_frames, start=1):
            gif_frame = add_rounded_corners(gif_frame, radius)

            canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
            gif_w, gif_h = gif_frame.size
            pos_x = (frame_w - gif_w) // 2
            pos_y = (frame_h - gif_h) // 2
            canvas.paste(gif_frame, (pos_x, pos_y), gif_frame)

            combined = Image.alpha_composite(frame, canvas)
            processed_frames.append(combined)
            
            # Update progress (second half of the process)
            progress = 50 + int((i / total_frames) * 50)
            self.signals.progress.emit(progress)
        
        self.signals.status.emit("Saving output GIF...")
        
        processed_frames[0].save(
            output_path,
            save_all=True,
            append_images=processed_frames[1:],
            optimize=False,
            duration=100,
            loop=0
        )

class FrameGifApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to find the frame.png in different locations
        self.frame_path = self.find_frame_png()
        self.logo_path = self.find_logo_png()
        self.gif_path = ""
        self.output_path = os.path.join(os.path.expanduser("~"), 'framed.gif')
        
        # Apply global stylesheet
        self.apply_stylesheet()
        
        self.init_ui()
        
    def apply_stylesheet(self):
        # Global application stylesheet
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {AppColors.BG_LIGHT};
                color: {AppColors.TEXT_DARK};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {AppColors.BG_DARK};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {AppColors.PRIMARY};
            }}
            
            QPushButton {{
                background-color: {AppColors.PRIMARY};
                color: {AppColors.TEXT_LIGHT};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }}
            
            QPushButton:hover {{
                background-color: {AppColors.PRIMARY_DARK};
            }}
            
            QPushButton:pressed {{
                background-color: {AppColors.PRIMARY_DARK};
                padding: 9px 15px 7px 17px;
            }}
            
            QLineEdit {{
                padding: 6px;
                border: 1px solid {AppColors.BG_DARK};
                border-radius: 4px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {AppColors.PRIMARY};
            }}
            
            QProgressBar {{
                border: 1px solid {AppColors.BG_DARK};
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }}
            
            QProgressBar::chunk {{
                background-color: {AppColors.PRIMARY};
                border-radius: 3px;
            }}
        """)
        
    def find_frame_png(self):
        # First check if frame.png is in the current directory
        local_frame = os.path.join(self.script_dir, 'frame.png')
        if os.path.exists(local_frame):
            return local_frame
            
        # Then check if it's available as a package resource
        try:
            frame_path = pkg_resources.resource_filename('frame_tool', 'frame.png')
            if os.path.exists(frame_path):
                return frame_path
        except:
            pass
            
        # If running as a bundled app, check relative to the executable
        if getattr(sys, 'frozen', False):
            bundle_dir = os.path.dirname(sys.executable)
            bundled_frame = os.path.join(bundle_dir, 'frame.png')
            if os.path.exists(bundled_frame):
                return bundled_frame
                
        # Default to the current directory and show a warning later if not found
        return os.path.join(self.script_dir, 'frame.png')
    
    def find_logo_png(self):
        # Check if logo.png is in the current directory
        local_logo = os.path.join(self.script_dir, 'logo.png')
        if os.path.exists(local_logo):
            return local_logo
            
        # If running as a bundled app, check relative to the executable
        if getattr(sys, 'frozen', False):
            bundle_dir = os.path.dirname(sys.executable)
            bundled_logo = os.path.join(bundle_dir, 'logo.png')
            if os.path.exists(bundled_logo):
                return bundled_logo
                
        # Default to the current directory
        return os.path.join(self.script_dir, 'logo.png')
        
    def init_ui(self):
        self.setWindowTitle("GIF Framing Tool")
        self.setMinimumSize(600, 400)  # Increased height for the header
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with logo and text
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {AppColors.PRIMARY_LIGHT}; border-radius: 8px;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        
        logo_label = QLabel()
        if os.path.exists(self.logo_path):
            logo_pixmap = QPixmap(self.logo_path)
            # Scale logo to reasonable size
            logo_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Logo not found")
            logo_label.setStyleSheet(f"color: {AppColors.PRIMARY}; font-weight: bold;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        header_layout.addLayout(logo_layout)
        
        # Tagline
        tagline_label = QLabel("A Karun Pant Creation")
        tagline_label.setAlignment(Qt.AlignCenter)
        
        # Style the tagline to match the primary color
        font = QFont("Arial", 12)
        font.setBold(True)
        tagline_label.setFont(font)
        tagline_label.setStyleSheet(f"color: {AppColors.PRIMARY}; margin-top: 5px;")
        
        header_layout.addWidget(tagline_label)
        main_layout.addWidget(header_widget)
        
        # Input section
        input_group = QGroupBox("Input Settings")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        # GIF input
        gif_layout = QHBoxLayout()
        gif_label = QLabel("Input GIF:")
        gif_label.setMinimumWidth(80)
        gif_layout.addWidget(gif_label)
        
        self.gif_entry = QLineEdit()
        gif_layout.addWidget(self.gif_entry)
        
        gif_browse_btn = QPushButton("Browse...")
        gif_browse_btn.setFixedWidth(100)
        gif_browse_btn.clicked.connect(self.browse_gif)
        gif_layout.addWidget(gif_browse_btn)
        
        input_layout.addLayout(gif_layout)
        
        # Frame image
        frame_layout = QHBoxLayout()
        frame_label = QLabel("Frame Image:")
        frame_label.setMinimumWidth(80)
        frame_layout.addWidget(frame_label)
        
        self.frame_entry = QLineEdit()
        self.frame_entry.setText(self.frame_path)
        frame_layout.addWidget(self.frame_entry)
        
        frame_browse_btn = QPushButton("Browse...")
        frame_browse_btn.setFixedWidth(100)
        frame_browse_btn.clicked.connect(self.browse_frame)
        frame_layout.addWidget(frame_browse_btn)
        
        input_layout.addLayout(frame_layout)
        main_layout.addWidget(input_group)
        
        # Output section
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)
        
        output_file_layout = QHBoxLayout()
        output_label = QLabel("Output GIF:")
        output_label.setMinimumWidth(80)
        output_file_layout.addWidget(output_label)
        
        self.output_entry = QLineEdit()
        self.output_entry.setText(self.output_path)
        output_file_layout.addWidget(self.output_entry)
        
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.setFixedWidth(100)
        output_browse_btn.clicked.connect(self.browse_output)
        output_file_layout.addWidget(output_browse_btn)
        
        output_layout.addLayout(output_file_layout)
        main_layout.addWidget(output_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to process")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"font-weight: bold; color: {AppColors.PRIMARY};")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        process_btn = QPushButton("Process GIF")
        process_btn.setMinimumWidth(150)
        process_btn.setMinimumHeight(40)
        process_btn.clicked.connect(self.process_gif)
        button_layout.addWidget(process_btn)
        
        main_layout.addLayout(button_layout)
        
        # Check if frame.png exists
        if not os.path.exists(self.frame_path):
            QMessageBox.warning(self, "Warning", 
                "Default frame.png not found. Please select a frame image manually.")
    
    def browse_gif(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input GIF", "", "GIF files (*.gif);;All files (*.*)"
        )
        if file_path:
            self.gif_path = file_path
            self.gif_entry.setText(file_path)
    
    def browse_frame(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Frame Image", "", "PNG files (*.png);;All files (*.*)"
        )
        if file_path:
            self.frame_path = file_path
            self.frame_entry.setText(file_path)
    
    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output GIF", "", "GIF files (*.gif);;All files (*.*)"
        )
        if file_path:
            self.output_path = file_path
            self.output_entry.setText(file_path)
    
    def process_gif(self):
        # Get the current values from entries
        self.gif_path = self.gif_entry.text()
        self.frame_path = self.frame_entry.text()
        self.output_path = self.output_entry.text()
        
        # Validate inputs
        if not self.gif_path or not os.path.exists(self.gif_path):
            QMessageBox.critical(self, "Error", "Please select a valid input GIF file.")
            return
            
        if not self.frame_path or not os.path.exists(self.frame_path):
            QMessageBox.critical(self, "Error", "Please select a valid frame image file.")
            return
            
        if not self.output_path:
            QMessageBox.critical(self, "Error", "Please specify an output path.")
            return
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting processing...")
        
        # Start processing in a separate thread
        self.processor = GifProcessor(self.gif_path, self.frame_path, self.output_path)
        self.processor.signals.progress.connect(self.update_progress)
        self.processor.signals.status.connect(self.update_status)
        self.processor.signals.finished.connect(self.processing_complete)
        self.processor.signals.error.connect(self.processing_error)
        self.processor.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def processing_complete(self, output_path, elapsed_time):
        self.status_label.setText(f"Done! Processing time: {elapsed_time:.2f} seconds")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {AppColors.SUCCESS};")
        
        # Create a custom message box with an option to open the folder
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Success")
        msg_box.setText(f"GIF successfully processed and saved to:\n{output_path}")
        
        # Add a button to open the containing folder
        open_folder_btn = msg_box.addButton("Go to File", QMessageBox.ActionRole)
        close_btn = msg_box.addButton(QMessageBox.Close)
        
        msg_box.exec_()
        
        # Check which button was clicked
        if msg_box.clickedButton() == open_folder_btn:
            self.open_containing_folder(output_path)
    
    def processing_error(self, error_message):
        self.status_label.setText("Error occurred during processing.")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {AppColors.ERROR};")
        
        QMessageBox.critical(self, "Error", f"Error processing GIF: {error_message}")
    
    def open_containing_folder(self, file_path):
        """Open the folder containing the file"""
        try:
            folder_path = os.path.dirname(os.path.abspath(file_path))
            
            if sys.platform == 'win32':
                # On Windows, use explorer to open the folder
                subprocess.run(['explorer', folder_path])
            elif sys.platform == 'darwin':  # macOS
                # On macOS, use 'open' command
                subprocess.run(['open', folder_path])
            else:  # Linux and other Unix-like
                # On Linux, use xdg-open
                subprocess.run(['xdg-open', folder_path])
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open the containing folder: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = FrameGifApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()