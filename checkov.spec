# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect non-code file from dependencies (JSON files, YAML files etc)
datas = collect_data_files('hcl2')
datas += collect_data_files('license_expression')
datas += collect_data_files('spdx')
datas += collect_data_files('pycep')
datas += collect_data_files('detect_secrets')
datas += collect_data_files('policyuniverse')
datas += collect_data_files('policy_sentry')
datas += collect_data_files('cloudsplaining')

# Collect all files under checkov dir into the package - graph YAML policies, lazy imports etc
datas += [
    ("checkov", "checkov"),
]

# Collect imports which are not stated explicitly or are lazy loaded
hidden_imports = ['policyuniverse', 'cloudsplaining']
hidden_imports += collect_submodules('detect_secrets.plugins')
hidden_imports += collect_submodules('policyuniverse.policy')
hidden_imports += collect_submodules('cloudsplaining.scan')


## From here to the bottom - default settings

block_cipher = None

a = Analysis(
    ['checkov/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='checkov',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
