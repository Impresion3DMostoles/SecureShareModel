# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SecureShareModelViewer.py'],
    pathex=[],
    binaries=[],
    datas=[('SSMLogo.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure, a.zipped_data)

#https://github.com/pyinstaller/pyinstaller/issues/2270#issuecomment-406575832
#Remove unused libs
Key = ['libcrypto']

def remove_from_list(input, keys):
    outlist = []
    for item in input:
        name, _, _ = item
        flag = 0
        for key_word in keys:
            if name.find(key_word) > -1:
                flag = 1
        if flag != 1:
            outlist.append(item)
    return outlist

a.binaries = remove_from_list(a.binaries, Key)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='SecureShareModelViewer',
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
    icon=['SSMLogo.png'],
)
