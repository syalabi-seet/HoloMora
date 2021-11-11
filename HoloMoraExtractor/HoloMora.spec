# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('functions.py', '.'), ('Romaji2Kana.py', '.'), ('ffmpeg.exe', '.'), ('models\\acoustic_model.h5', '.'), ('models\\acoustic_vocab.json', '.'), ('models\\bert_model.h5', '.'), ('models\\bert_vocab.txt', '.')]
datas += collect_data_files('ipadic')
datas += collect_data_files('tensorflow')
datas += collect_data_files('torch')
datas += copy_metadata('ipadic')
datas += copy_metadata('tensorflow')
datas += copy_metadata('torch')
datas += copy_metadata('tqdm')
datas += copy_metadata('regex')
datas += copy_metadata('sacremoses')
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('filelock')
datas += copy_metadata('numpy')
datas += copy_metadata('tokenizers')
datas += copy_metadata('importlib_metadata')


block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=['ipadic', 'pkg_resources.py2_warn', 'tensorflow', 'pytorch'],
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
          name='HoloMora',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='HoloMora')
