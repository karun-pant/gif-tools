import threading
import time
from PIL import Image, ImageDraw, ImageSequence

class GifProcessor(threading.Thread):
    def __init__(self, gif_path, frame_path, output_path, signals):
        super().__init__()
        self.gif_path = gif_path
        self.frame_path = frame_path
        self.output_path = output_path
        self.signals = signals
        
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
                progress = 10 + int((i / total_frames) * 40)  # Start at 10% (after video conversion)
                self.signals.progress.emit(progress)
        
        return frames
    
    def overlay_gif_on_frame(self, frame_path, gif_frames, output_path):
        radius = 275
        frame = Image.open(frame_path).convert("RGBA")
        frame_w, frame_h = frame.size

        processed_frames = []
        total_frames = len(gif_frames)
        
        for i, gif_frame in enumerate(gif_frames, start=1):
            gif_frame = self.add_rounded_corners(gif_frame, radius)

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
    
    @staticmethod
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