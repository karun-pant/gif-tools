import os
import subprocess
import tempfile
import sys
from PIL import Image

# Try to import imageio and its ffmpeg plugin
try:
    import imageio
    IMAGEIO_AVAILABLE = True
    
    # Try to import the ffmpeg plugin
    try:
        import imageio_ffmpeg
        FFMPEG_AVAILABLE = True
    except ImportError:
        FFMPEG_AVAILABLE = False
except ImportError:
    IMAGEIO_AVAILABLE = False
    FFMPEG_AVAILABLE = False

class VideoConverter:
    """Handles conversion of video files (MP4, MOV) to GIF format."""
    
    def __init__(self, signals=None):
        self.signals = signals
        self.ffmpeg_available = FFMPEG_AVAILABLE
    
    def convert_to_gif(self, video_path, output_gif_path=None, fps=10, quality=90):
        """
        Convert a video file to GIF format.
        
        Args:
            video_path: Path to the input video file
            output_gif_path: Path for the output GIF (if None, creates a temporary file)
            fps: Frames per second to capture
            quality: Quality of the output GIF (0-100)
            
        Returns:
            Path to the created GIF file
        """
        if self.signals:
            self.signals.status.emit(f"Converting video to GIF...")
            self.signals.progress.emit(5)
        
        # If no output path specified, create a temporary file
        if not output_gif_path:
            temp_dir = tempfile.gettempdir()
            output_gif_path = os.path.join(temp_dir, f"temp_converted_{os.path.basename(video_path)}.gif")
        
        try:
            # Check if imageio is available
            if not IMAGEIO_AVAILABLE:
                raise ImportError("The 'imageio' module is required for video conversion. "
                                 "Please install it with 'pip install imageio[ffmpeg]'.")
            
            # Check if ffmpeg plugin is available
            if not self.ffmpeg_available:
                self.signals.status.emit("FFMPEG plugin not found, installing...")
                # Try to install the ffmpeg plugin
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio[ffmpeg]"])
                    
                    # Try importing again
                    try:
                        import imageio_ffmpeg
                        self.ffmpeg_available = True
                        self.signals.status.emit("FFMPEG plugin installed successfully")
                    except ImportError:
                        self.signals.status.emit("FFMPEG plugin installation failed")
                except Exception as e:
                    self.signals.status.emit(f"Could not install FFMPEG plugin: {str(e)}")
                    # Try alternative method
                    return self._convert_with_alternative_method(video_path, output_gif_path, fps)
            
            # Try to convert with imageio
            try:
                self._convert_with_imageio(video_path, output_gif_path, fps)
            except Exception as e:
                self.signals.status.emit(f"Error with imageio: {str(e)}")
                # Try alternative method
                return self._convert_with_alternative_method(video_path, output_gif_path, fps)
            
            if self.signals:
                self.signals.status.emit(f"Video successfully converted to GIF")
                self.signals.progress.emit(10)
                
            return output_gif_path
            
        except Exception as e:
            if self.signals:
                self.signals.error.emit(f"Error converting video: {str(e)}")
            raise
    
    def _convert_with_imageio(self, video_path, output_gif_path, fps):
        """Convert video to GIF using imageio library"""
        self.signals.status.emit(f"Reading video with imageio...")
        reader = imageio.get_reader(video_path)
        fps_source = reader.get_meta_data().get('fps', 30)  # Default to 30 if not found
        
        # Calculate frame step to achieve target fps
        step = max(1, int(fps_source / fps))
        
        frames = []
        total_frames = 0
        
        # Try to get total frames count
        try:
            total_frames = reader.count_frames()
        except:
            # If count_frames() is not available, we'll just update progress differently
            pass
        
        self.signals.status.emit(f"Extracting frames...")
        frame_count = 0
        
        for i, frame in enumerate(reader):
            if i % step == 0:
                frames.append(frame)
                frame_count += 1
                
                if self.signals and total_frames > 0:
                    progress = 5 + int((i / total_frames) * 5)
                    self.signals.progress.emit(min(10, progress))
                elif self.signals and i % 10 == 0:  # Update every 10 frames if total unknown
                    self.signals.progress.emit(min(10, 5 + (frame_count % 5)))
        
        self.signals.status.emit(f"Saving GIF with {len(frames)} frames...")
        imageio.mimsave(output_gif_path, frames, fps=fps)
    
    def _convert_with_alternative_method(self, video_path, output_gif_path, fps):
        """Try to convert using ffmpeg directly if available"""
        self.signals.status.emit("Trying alternative conversion method with ffmpeg...")
        
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # Create a palette for better quality
            palette_path = os.path.join(tempfile.gettempdir(), "palette.png")
            
            # Generate palette
            subprocess.run([
                'ffmpeg', '-i', video_path, 
                '-vf', f'fps={fps},scale=320:-1:flags=lanczos,palettegen', 
                palette_path
            ], check=True)
            
            # Convert to GIF using the palette
            subprocess.run([
                'ffmpeg', '-i', video_path, 
                '-i', palette_path,
                '-filter_complex', f'fps={fps},scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse', 
                output_gif_path
            ], check=True)
            
            self.signals.status.emit("Video converted with ffmpeg")
            return output_gif_path
            
        except subprocess.CalledProcessError as e:
            self.signals.status.emit(f"FFMPEG error: {str(e)}")
            raise RuntimeError(f"Failed to convert video. Please install imageio[ffmpeg] with: pip install 'imageio[ffmpeg]'")
            
        except FileNotFoundError:
            self.signals.status.emit("FFMPEG not found")
            raise RuntimeError("FFMPEG not found. Please install imageio[ffmpeg] with: pip install 'imageio[ffmpeg]'")