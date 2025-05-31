# Install PyInstaller if you haven't already
pip install pyinstaller

cd frame-tool 

# Build the app using the spec file
pyinstaller FrameGifTool.spec

# The app will be created in the dist directory
# You can zip it for distribution
cd dist
zip -r FrameGifTool-Mac.zip FrameGifTool.app