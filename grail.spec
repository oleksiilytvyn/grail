# -*- mode: python ; coding: utf-8 -*-

arch = "NA"
version = "1.0"
block_cipher = None

a = Analysis(['grail.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

import grail
import platform

version = grail.__version__
version_tuple = ", ".join(str(x) for x in (version.split('.') + [0, 0, 0, 0])[0:4])
arch = platform.architecture()[0]

VERSION_FILE = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
  StringFileInfo(
  [
    StringTable(u'040904B0', [
      StringStruct(u'CompanyName', u'Oleksii Lytvyn'),
      StringStruct(u'FileDescription', u'Grail'),
      StringStruct(u'FileVersion', u'{version}'),
      StringStruct(u'InternalName', u'Grail'),
      StringStruct(u'LegalCopyright', u'Copyright (c) Oleksii Lytvyn'),
      StringStruct(u'OriginalFilename', u'grail.exe'),
      StringStruct(u'ProductName', u'Grail'),
      StringStruct(u'ProductVersion', u'{version}')
      ])
    ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

file = open("version.rc", "w")
file.write(VERSION_FILE)
file.close()

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Grail %s (%s)' % (version, arch),
          icon = "./data/icon/grail.ico",
          version="./version.rc",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )

app = BUNDLE(exe,
         name='Grail.app',
         icon=None,
         bundle_identifier=None,
         info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False
            },
         )