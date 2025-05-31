# GIF Framing Tool

A simple tool for framing GIFs with device frames. This tool allows you to overlay animated GIFs onto a device frame image, creating a professional-looking presentation of your mobile app or website animations.

## Features

- Overlay animated GIFs onto device frames
- Automatically resize GIFs to fit the frame
- Apply rounded corners to match device screens
- Simple and intuitive GUI interface
- Cross-platform (Windows, macOS, Linux)

## Installation

### Option 1: Download the Executable (Recommended for most users)

1. Download the latest release from the [Releases](https://github.com/karun-pant/gif-tools/releases) page
2. Extract the zip file to a location of your choice
3. Run the executable:
   - Windows: Double-click `FrameGifTool.exe`
   - macOS: Right-click on `FrameGifTool`, select "Open" (you may need to approve it in Security settings)
   - Linux: Make the file executable with `chmod +x FrameGifTool` and then run it with `./FrameGifTool`

### Option 2: Install as a Python Package

If you have Python installed (3.6 or later), you can install the tool as a package:

```bash
pip install frame-gif-tool
```

Then run it with:

```bash
frame-gif
```

### Option 3: Run from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/karun-pant/gif-tools.git
   cd gif-tools/frame-tool
   ```

2. Install the required dependencies:
   ```bash
   pip install PyQt5 Pillow
   ```

3. Run the script:
   ```bash
   python frameGif.py
   ```

## Usage

1. Launch the GIF Framing Tool
2. Select your input GIF using the "Browse..." button
3. (Optional) Choose a custom frame image, or use the default frame
4. Specify the output location for your framed GIF
5. Click "Process GIF" to start the framing process
6. Once complete, the framed GIF will automatically open in your default image viewer

## Building from Source

If you want to build the executable yourself:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_app.py
   ```

3. Find the executable in the `dist` folder

## Requirements

- Python 3.6 or higher (for running from source or as a package)
- PyQt5
- Pillow (PIL Fork)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The default frame image is designed for demonstration purposes
- For best results, use GIFs that match the aspect ratio of the device screen