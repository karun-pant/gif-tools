import os
import sys
import time
import threading
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
from PIL import Image, ImageDraw, ImageSequence
import io

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
        
        # Default paths
        self.frame_path = os.path.join(self.script_dir, 'frame.png')
        self.gif_path = ""
        self.output_path = os.path.join(self.script_dir, 'framed.gif')
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("GIF Framing Tool")
        self.setMinimumSize(600, 300)  # Reduced size since we removed the preview
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Input section
        input_group = QGroupBox("Input Settings")
        input_layout = QVBoxLayout(input_group)
        
        # GIF input
        gif_layout = QHBoxLayout()
        gif_layout.addWidget(QLabel("Input GIF:"))
        self.gif_entry = QLineEdit()
        gif_layout.addWidget(self.gif_entry)
        gif_browse_btn = QPushButton("Browse...")
        gif_browse_btn.clicked.connect(self.browse_gif)
        gif_layout.addWidget(gif_browse_btn)
        input_layout.addLayout(gif_layout)
        
        # Frame image
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(QLabel("Frame Image:"))
        self.frame_entry = QLineEdit()
        self.frame_entry.setText(self.frame_path)
        frame_layout.addWidget(self.frame_entry)
        frame_browse_btn = QPushButton("Browse...")
        frame_browse_btn.clicked.connect(self.browse_frame)
        frame_layout.addWidget(frame_browse_btn)
        input_layout.addLayout(frame_layout)
        
        main_layout.addWidget(input_group)
        
        # Output section
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(QLabel("Output GIF:"))
        self.output_entry = QLineEdit()
        self.output_entry.setText(self.output_path)
        output_file_layout.addWidget(self.output_entry)
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_output)
        output_file_layout.addWidget(output_browse_btn)
        output_layout.addLayout(output_file_layout)
        
        main_layout.addWidget(output_group)
        
        # Progress section
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addLayout(progress_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        process_btn = QPushButton("Process GIF")
        process_btn.clicked.connect(self.process_gif)
        button_layout.addWidget(process_btn)
        
        main_layout.addLayout(button_layout)
    
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
        QMessageBox.information(self, "Success", f"GIF successfully processed and saved to:\n{output_path}")
        
        # Open the processed GIF with the system's default application
        self.open_with_default_app(output_path)
    
    def processing_error(self, error_message):
        self.status_label.setText("Error occurred during processing.")
        QMessageBox.critical(self, "Error", f"Error processing GIF: {error_message}")
    
    def open_with_default_app(self, file_path):
        """Open the file with the system's default application"""
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux and other Unix-like
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open the file with default application: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrameGifApp()
    window.show()
    sys.exit(app.exec_())