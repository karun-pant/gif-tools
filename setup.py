import os
import sys
from setuptools import setup, find_packages

APP_NAME = "GIF Framing Tool"
APP_VERSION = "1.0.0"
AUTHOR = "Karun Pant"
DESCRIPTION = "A tool to frame GIFs and videos in device frames"

# Dependencies
INSTALL_REQUIRES = [
    "PyQt5>=5.15.0",
    "Pillow>=8.0.0",
    "imageio>=2.9.0",
    "imageio-ffmpeg>=0.4.0",
]

setup(
    name=APP_NAME.replace(" ", "_").lower(),
    version=APP_VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.6",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "gifframingtool=main:main",
        ],
    },
)