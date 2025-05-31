from PIL import Image, ImageDraw, ImageSequence
import sys

def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()  # New line on complete

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
        print("Resizing GIF frames:")
        for i, frame in enumerate(ImageSequence.Iterator(im), start=1):
            frame = frame.convert("RGBA")
            frame = frame.resize(target_size, Image.Resampling.LANCZOS)
            frames.append(frame)
            print_progress_bar(i, total_frames)
    return frames

def overlay_gif_on_frame(frame_path, gif_frames, output_path):
    radius = 275
    frame = Image.open(frame_path).convert("RGBA")
    frame_w, frame_h = frame.size

    processed_frames = []
    total_frames = len(gif_frames)
    print("Overlaying frames on background:")
    for i, gif_frame in enumerate(gif_frames, start=1):
        gif_frame = add_rounded_corners(gif_frame, radius)

        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        gif_w, gif_h = gif_frame.size
        pos_x = (frame_w - gif_w) // 2
        pos_y = (frame_h - gif_h) // 2
        canvas.paste(gif_frame, (pos_x, pos_y), gif_frame)

        combined = Image.alpha_composite(frame, canvas)
        processed_frames.append(combined)

        print_progress_bar(i, total_frames)

    print("Saving output GIF...")
    processed_frames[0].save(
        output_path,
        save_all=True,
        append_images=processed_frames[1:],
        optimize=False,
        duration=100,
        loop=0
    )
    print("Done saving output GIF.")

# Usage example
frame_path = 'frame.png'
gif_path = 'plain_output.gif'
output_path = 'output.gif'


gif_frames = resize_gif_frames(gif_path)
overlay_gif_on_frame(frame_path, gif_frames, output_path)
