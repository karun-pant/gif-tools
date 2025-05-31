import os
import sys
import shutil
import subprocess
import platform
from PIL import Image
import tempfile

def create_icns_from_png(png_path):
    """Convert a PNG file to ICNS format for macOS app icon"""
    if not os.path.exists(png_path):
        print(f"Warning: Logo file not found at {png_path}")
        return None
        
    # Create a temporary directory for the iconset
    with tempfile.TemporaryDirectory() as temp_dir:
        iconset_path = os.path.join(temp_dir, "AppIcon.iconset")
        os.makedirs(iconset_path, exist_ok=True)
        
        # Open the original image
        img = Image.open(png_path)
        
        # Create icons of different sizes
        icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in icon_sizes:
            # Regular size
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            resized_img.save(os.path.join(iconset_path, f"icon_{size}x{size}.png"))
            
            # @2x size (for Retina displays)
            if size * 2 <= 1024:  # Don't exceed 1024
                resized_img = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
                resized_img.save(os.path.join(iconset_path, f"icon_{size}x{size}@2x.png"))
        
        # Create the .icns file
        icns_path = os.path.join(temp_dir, "AppIcon.icns")
        
        if platform.system() == "Darwin":
            # On macOS, use the iconutil command
            subprocess.run(["iconutil", "-c", "icns", iconset_path, "-o", icns_path], check=True)
        else:
            # On other platforms, we can't create a proper .icns file
            # Just copy the largest PNG as a placeholder
            shutil.copy(
                os.path.join(iconset_path, f"icon_{icon_sizes[-1]}x{icon_sizes[-1]}.png"),
                icns_path.replace(".icns", ".png")
            )
            icns_path = icns_path.replace(".icns", ".png")
        
        # Copy the icon to the project directory
        dest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AppIcon.icns")
        shutil.copy(icns_path, dest_path)
        
        return dest_path

def build_app():
    """Build the application into a standalone executable"""
    print("Building GIF Framing Tool...")
    
    # Determine the platform
    system = platform.system()
    
    # Clean up previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Create app icon from logo.png
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    icon_path = None
    
    try:
        icon_path = create_icns_from_png(logo_path)
        print(f"Created app icon at: {icon_path}")
    except Exception as e:
        print(f"Warning: Could not create app icon: {e}")
    
    # Create a spec file for PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frame.png', '.'),
        ('logo.png', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if """ + repr(system == "Darwin") + """:
    # macOS specific settings
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='GIF Framing Tool',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='GIF Framing Tool',
    )
    
    app = BUNDLE(
        coll,
        name='GIF Framing Tool.app',
        icon=""" + (f"'{icon_path}'" if icon_path else "None") + """,
        bundle_identifier='com.karunpant.gifframingtool',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDisplayName': 'GIF Framing Tool',
            'CFBundleName': 'GIF Framing Tool',
            'CFBundleGetInfoString': 'A tool to frame GIFs and videos in device frames',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
else:
    # Windows/Linux settings
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='GIF Framing Tool',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=""" + (f"'{icon_path}'" if icon_path and system != "Darwin" else "None") + """,
    )
"""
    
    # Write the spec file
    with open("gifframingtool.spec", "w") as f:
        f.write(spec_content)
    
    # Install PyInstaller if not already installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller. Please install it manually with:")
        print("pip install pyinstaller")
        return False
    
    # Run PyInstaller
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "PyInstaller", 
            "gifframingtool.spec", 
            "--clean"
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error building application: {e}")
        return False
    
    # Check if build was successful
    if system == "Darwin":
        app_path = os.path.join("dist", "GIF Framing Tool.app")
        if os.path.exists(app_path):
            print(f"Application built successfully at: {os.path.abspath(app_path)}")
            return True
    else:
        exe_path = os.path.join("dist", "GIF Framing Tool.exe" if system == "Windows" else "GIF Framing Tool")
        if os.path.exists(exe_path):
            print(f"Application built successfully at: {os.path.abspath(exe_path)}")
            return True
    
    print("Build failed. Check the output for errors.")
    return False

if __name__ == "__main__":
    build_app()