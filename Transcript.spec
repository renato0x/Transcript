# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['transcript.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.ico', '.'), ('style.qss', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'torch',
        'transformers',
        'scipy',
        'sympy',
        'jinja2',
        'tensorflow',
        'tensorboard',
        'matplotlib',
        'networkx',
        'pandas',
        'numpy.testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Transcript',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='logo.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Transcript',
)
