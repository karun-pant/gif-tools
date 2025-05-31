# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['frameGif.py'],
             pathex=[],
             binaries=[],
             datas=[('frame.png', 'logo.png', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='FrameGifTool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='FrameGifTool')

app = BUNDLE(coll,
             name='FrameGifTool.app',
             icon=None,
             bundle_identifier='com.karunpant.framegiftool',
             info_plist={
                'NSHighResolutionCapable': 'True',
                'CFBundleShortVersionString': '1.0.0',
                'CFBundleVersion': '1.0.0',
                'NSHumanReadableCopyright': '© 2023 Karun Pant'
             })