# Frame GIF Tool

A simple tool for framing GIFs with device frames.

## Installation

### Using pip

```bash
pip install frame-gif-tool
```

### From source

```bash
git clone https://github.com/karun-pant/gif-tools.git
cd gif-tools
pip install -e .
```

## Usage

After installation, you can run the tool in two ways:

1. Command line:
```bash
frame-gif
```

2. As an application:
```bash
frame-gif-app
```

## Features

- Load any GIF and overlay it on a device frame
- Automatically resizes GIF to fit the frame
- Adds rounded corners to match device aesthetics
- Saves the framed GIF to your desired location

## Mac App

A standalone Mac application is available for download from the [releases page](https://github.com/karun-pant/gif-tools/releases).

## License

MIT
```

3. Create a LICENSE file:

```bash
touch LICENSE
```

4. Add MIT license content:

```text:LICENSE
MIT License

Copyright (c) 2023 Karun Pant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 5. Create a MANIFEST.in file

```bash
touch MANIFEST.in
```

Add content:

```text:MANIFEST.in
include LICENSE
include README.md
include frame.png
```

## 6. Distribution Steps

### A. PyPI Distribution

1. Install build tools:

```bash
pip install build twine
```

2. Build the package:

```bash
python -m build
```

3. Upload to PyPI:

```bash
python -m twine upload dist/*
```

### B. GitHub Distribution

1. Create a GitHub repository if you don't have one already
2. Initialize git and push your code:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/karun-pant/gif-tools.git
git push -u origin main
```

3. Create a GitHub release with the Mac app:

```bash
# Compress the Mac app for distribution
cd dist
zip -r FrameGifTool-Mac.zip FrameGifTool.app
```

4. Go to GitHub, create a new release, and upload the `FrameGifTool-Mac.zip` file.

## 7. GitHub Actions for Automated Builds (Optional)

Create a GitHub Actions workflow to automatically build the Mac app:

```bash
mkdir -p .github/workflows
touch .github/workflows/build-mac-app.yml
```

Add content:

```yaml:.github/workflows/build-mac-app.yml
name: Build Mac App

on:
   push:
     tags:
       - 'v*'

jobs:
   build:
     runs-on: macos-latest
    
     steps:
     - uses: actions/checkout@v2
    
     - name: Set up Python
       uses: actions/setup-python@v2
       with:
         python-version: '3.9'
    
     - name: Install dependencies
       run: |
         python -m pip install --upgrade pip
         pip install pyinstaller
         pip install -e .
    
     - name: Build Mac App
       run: |
         pyinstaller FrameGifTool.spec
         cd dist
         zip -r FrameGifTool-Mac.zip FrameGifTool.app
    
     - name: Create Release
       id: create_release
       uses: actions/create-release@v1
       env:
         GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       with:
         tag_name: ${{ github.ref }}
         release_name: Release ${{ github.ref }}
         draft: false
         prerelease: false
    
     - name: Upload Release Asset
       uses: actions/upload-release-asset@v1
       env:
         GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       with:
         upload_url: ${{ steps.create_release.outputs.upload_url }}
         asset_path: ./dist/FrameGifTool-Mac.zip
         asset_name: FrameGifTool-Mac.zip
         asset_content_type: application/zip
```