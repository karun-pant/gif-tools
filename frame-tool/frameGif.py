from PIL import Image, ImageDraw, ImageSequence
import sys
import os
import time
import threading

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored(text, color):
    """Add color to text"""
    return f"{color}{text}{Colors.ENDC}"

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, color=Colors.BLUE):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = colored('█' * filled_length, color) + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {colored(percent + "%", color)} {suffix}', end='\r')
    if iteration == total:
        print()  # New line on complete

def animated_loading(stop_event, message="Processing", color=Colors.CYAN):
    """Display an animated loading indicator"""
    animation = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # More elegant spinner
    idx = 0
    while not stop_event.is_set():
        print(f"\r{colored(message, color)} {colored(animation[idx % len(animation)], color)}", end="")
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * (len(message) + 2), end="\r")  # Clear the line

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

def resize_gif_frames(input_gif):
    target_size = (2257, 4854)
    with Image.open(input_gif) as im:
        frames = []
        total_frames = im.n_frames
        print(colored("Resizing GIF frames:", Colors.HEADER))
        for i, frame in enumerate(ImageSequence.Iterator(im), start=1):
            frame = frame.convert("RGBA")
            frame = frame.resize(target_size, Image.Resampling.LANCZOS)
            frames.append(frame)
            print_progress_bar(i, total_frames, color=Colors.BLUE)
    return frames

def overlay_gif_on_frame(frame_path, gif_frames, output_path):
    radius = 275
    frame = Image.open(frame_path).convert("RGBA")
    frame_w, frame_h = frame.size

    processed_frames = []
    total_frames = len(gif_frames)
    print(colored("Overlaying frames on background:", Colors.HEADER))
    for i, gif_frame in enumerate(gif_frames, start=1):
        gif_frame = add_rounded_corners(gif_frame, radius)

        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        gif_w, gif_h = gif_frame.size
        pos_x = (frame_w - gif_w) // 2
        pos_y = (frame_h - gif_h) // 2
        canvas.paste(gif_frame, (pos_x, pos_y), gif_frame)

        combined = Image.alpha_composite(frame, canvas)
        processed_frames.append(combined)

        print_progress_bar(i, total_frames, color=Colors.CYAN)

    print(colored("Saving output GIF...", Colors.HEADER))
    
    # Start the loading animation in a separate thread
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=animated_loading, args=(stop_event, "Saving GIF", Colors.YELLOW))
    loading_thread.daemon = True
    loading_thread.start()
    
    try:
        processed_frames[0].save(
            output_path,
            save_all=True,
            append_images=processed_frames[1:],
            optimize=False,
            duration=100,
            loop=0
        )
    finally:
        # Stop the loading animation
        stop_event.set()
        loading_thread.join()
        
    print(colored("Done saving output GIF.", Colors.GREEN))

def get_valid_file_path(prompt, file_must_exist=True):
    while True:
        file_path = input(colored(prompt, Colors.YELLOW))
        file_path = file_path.strip()
        
        # If user just presses Enter, return None to use default
        if not file_path:
            return None
            
        # Check if file exists if required
        if file_must_exist and not os.path.exists(file_path):
            print(colored(f"Error: File '{file_path}' does not exist. Please enter a valid path.", Colors.RED))
            continue
            
        return file_path

def main():
    # Print a nice header
    print(colored("\n╔═══════════════════════════════════════╗", Colors.CYAN))
    print(colored("║        GIF FRAMING TOOL               ║", Colors.CYAN))
    print(colored("╚═══════════════════════════════════════╝\n", Colors.CYAN))
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Default paths
    frame_path = 'frame.png'
    default_gif_path = 'plain_output.gif'
    output_path = 'framed.gif'
    
    # Ask for GIF path
    print(colored(f"Default GIF path: {default_gif_path}", Colors.BLUE))
    gif_path = get_valid_file_path("Enter path to input GIF file (or press Enter for default): ", True)
    if not gif_path:
        gif_path = default_gif_path
        if not os.path.exists(gif_path):
            print(colored(f"Error: Default GIF file not found at '{gif_path}'", Colors.RED))
            return
    
    print(colored("\nProcessing with:", Colors.HEADER))
    print(colored(f"Frame: {frame_path}", Colors.GREEN))
    print(colored(f"Input GIF: {gif_path}", Colors.GREEN))
    print(colored(f"Output: {output_path}", Colors.GREEN))
    print()
    
    # Process the GIF
    try:
        start_time = time.time()
        gif_frames = resize_gif_frames(gif_path)
        overlay_gif_on_frame(frame_path, gif_frames, output_path)
        elapsed_time = time.time() - start_time
        print(colored(f"✓ Successfully created framed GIF at: {output_path}", Colors.GREEN))
        print(colored(f"Total processing time: {elapsed_time:.2f} seconds", Colors.BLUE))
    except Exception as e:
        print(colored(f"Error processing GIF: {str(e)}", Colors.RED))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\nProcess interrupted by user. Exiting...", Colors.YELLOW))
        sys.exit(0)
