import os
from PyInstaller.utils.hooks import (collect_data_files, collect_dynamic_libs,
                                     collect_submodules)

datas = [('images', 'images')]

if os.path.exists('Osher.ico'):
    datas += [('Osher.ico', '.')]

datas += collect_data_files('cmu_graphics', include_py_files=True)

binaries = collect_dynamic_libs('cairo') + collect_dynamic_libs('pygame')

hiddenimports = collect_submodules('cmu_graphics') + ['cairo', 'PIL.Image']

a = Analysis(
    ['Osher.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=['pyi_rth_osher.py'],
    excludes=['tkinter', 'numpy', 'matplotlib', 'scipy', 'pytest'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Osher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon='Osher.ico' if os.path.exists('Osher.ico') else None,
)
