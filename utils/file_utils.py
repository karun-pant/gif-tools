import os
import sys
import subprocess
import pkg_resources

def find_resource_path(filename, package_name='frame_tool'):
    """Find a resource file in various possible locations"""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(script_dir)  # Go up one level from utils/
    
    # First check if file is in the current directory
    local_path = os.path.join(script_dir, filename)
    if os.path.exists(local_path):
        return local_path
        
    # Then check if it's available as a package resource
    try:
        resource_path = pkg_resources.resource_filename(package_name, filename)
        if os.path.exists(resource_path):
            return resource_path
    except:
        pass
        
    # If running as a bundled app, check relative to the executable
    if getattr(sys, 'frozen', False):
        bundle_dir = os.path.dirname(sys.executable)
        bundled_path = os.path.join(bundle_dir, filename)
        if os.path.exists(bundled_path):
            return bundled_path
            
    # Default to the current directory
    return os.path.join(script_dir, filename)

def open_containing_folder(file_path):
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
            
        return True
    except Exception as e:
        return False, str(e)

def is_video_file(file_path):
    """Check if a file is a video file based on its extension"""
    if not file_path:
        return False
    
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv']
    ext = os.path.splitext(file_path.lower())[1]
    return ext in video_extensions

def is_gif_file(file_path):
    """Check if a file is a GIF file based on its extension"""
    if not file_path:
        return False
    
    return os.path.splitext(file_path.lower())[1] == '.gif'