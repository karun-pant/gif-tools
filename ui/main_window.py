import os
import threading  # Add this import
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
                            QMessageBox, QGroupBox, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

from utils.styles import AppColors
from utils.signals import WorkerSignals
from utils.file_utils import find_resource_path, open_containing_folder, is_video_file, is_gif_file
from processors.gif_processor import GifProcessor
from processors.video_converter import VideoConverter

class FrameGifApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize paths
        self.frame_path = find_resource_path('frame.png')
        self.logo_path = find_resource_path('logo.png')
        self.input_path = ""
        self.output_path = os.path.join(os.path.expanduser("~"), 'framed.gif')
        
        # Initialize signals
        self.signals = WorkerSignals()
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.signals.progress.connect(self.update_progress)
        self.signals.status.connect(self.update_status)
        self.signals.finished.connect(self.processing_complete)
        self.signals.error.connect(self.processing_error)
        
    def init_ui(self):
        self.setWindowTitle("GIF Framing Tool")
        self.setMinimumSize(600, 450)
        
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
        
        # Input file (GIF or Video)
        input_layout_row = QHBoxLayout()
        input_label = QLabel("Input File:")
        input_label.setMinimumWidth(80)
        input_layout_row.addWidget(input_label)
        
        self.input_entry = QLineEdit()
        input_layout_row.addWidget(self.input_entry)
        
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.setFixedWidth(100)
        input_browse_btn.clicked.connect(self.browse_input)
        input_layout_row.addWidget(input_browse_btn)
        
        input_layout.addLayout(input_layout_row)
        
        # Input type info
        input_type_layout = QHBoxLayout()
        self.input_type_label = QLabel("Supported formats: GIF, MP4, MOV")
        self.input_type_label.setStyleSheet(f"color: {AppColors.SECONDARY}; font-style: italic;")
        input_type_layout.addWidget(self.input_type_label)
        input_type_layout.addStretch()
        input_layout.addLayout(input_type_layout)
        
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
        
        process_btn = QPushButton("Process Media")
        process_btn.setMinimumWidth(150)
        process_btn.setMinimumHeight(40)
        process_btn.clicked.connect(self.process_media)
        button_layout.addWidget(process_btn)
        
        main_layout.addLayout(button_layout)
        
        # Check if frame.png exists
        if not os.path.exists(self.frame_path):
            QMessageBox.warning(self, "Warning", 
                "Default frame.png not found. Please select a frame image manually.")
    
    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", 
            "Media files (*.gif *.mp4 *.mov);;GIF files (*.gif);;Video files (*.mp4 *.mov);;All files (*.*)"
        )
        if file_path:
            self.input_path = file_path
            self.input_entry.setText(file_path)
            
            # Update output path with same name but .gif extension
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.dirname(self.output_entry.text())
            new_output = os.path.join(output_dir, f"{base_name}_framed.gif")
            self.output_entry.setText(new_output)
    
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
    
    def process_media(self):
        # Get the current values from entries
        self.input_path = self.input_entry.text()
        self.frame_path = self.frame_entry.text()
        self.output_path = self.output_entry.text()
        
        # Validate inputs
        if not self.input_path or not os.path.exists(self.input_path):
            QMessageBox.critical(self, "Error", "Please select a valid input file (GIF, MP4, or MOV).")
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
        self.process_thread = threading.Thread(target=self._process_media_thread)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def _process_media_thread(self):
        try:
            # Check if input is a video file
            gif_path = self.input_path
            
            if is_video_file(self.input_path):
                # Convert video to GIF first
                self.signals.status.emit("Converting video to GIF...")
                converter = VideoConverter(self.signals)
                gif_path = converter.convert_to_gif(self.input_path)
            
            # Now process the GIF
            processor = GifProcessor(gif_path, self.frame_path, self.output_path, self.signals)
            processor.run()  # Direct call instead of start() to keep in the same thread
            
        except Exception as e:
            self.signals.error.emit(str(e))
    
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
            open_containing_folder(output_path)
    
    def processing_error(self, error_message):
        self.status_label.setText("Error occurred during processing.")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {AppColors.ERROR};")
        
        QMessageBox.critical(self, "Error", f"Error processing media: {error_message}")