import os
import sys
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

# Define package metadata
NAME = "frame-gif-tool"
VERSION = "1.0.0"
DESCRIPTION = "A tool for framing GIFs with device frames"
LONG_DESCRIPTION = open("README.md").read() if os.path.exists("README.md") else DESCRIPTION
AUTHOR = "Karun Pant"
AUTHOR_EMAIL = ""
URL = "https://github.com/karun-pant/gif-tools"
PACKAGES = find_packages()
REQUIRED = [
    "PyQt5",
    "Pillow",
]

# Ensure the frame.png is included in the package
def include_frame_png(command_subclass):
    """A decorator for classes subclassing one of the setuptools commands.
    It modifies the run() method so that it includes the frame.png file
    in the package directory before installation.
    """
    orig_run = command_subclass.run

    def modified_run(self):
        # Make sure the frame.png is included
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frame_tool")
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy frame.png to the package directory
        frame_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frame.png")
        frame_dst = os.path.join(target_dir, "frame.png")
        if os.path.exists(frame_src):
            shutil.copy2(frame_src, frame_dst)
        else:
            print(f"Warning: frame.png not found at {frame_src}")
        
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass

@include_frame_png
class CustomInstallCommand(install):
    pass

@include_frame_png
class CustomDevelopCommand(develop):
    pass

@include_frame_png
class CustomEggInfoCommand(egg_info):
    pass

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=PACKAGES,
    install_requires=REQUIRED,
    include_package_data=True,
    package_data={
        'frame_tool': ['frame.png'],
    },
    entry_points={
        'console_scripts': [
            'frame-gif=frame_tool.frameGif:main',
        ],
        'gui_scripts': [
            'frame-gif-app=frame_tool.frameGif:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics',
    ],
    python_requires='>=3.6',
)