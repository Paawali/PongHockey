# -*- mode: python -*-

block_cipher = None

binary = [('/home/kone/PycharmProjects/PongHockey/venv/lib/python3.5/site-packages/pymunk/libchipmunk.so','.')]
files = [('/home/kone/PycharmProjects/PongHockey/data/*.*', 'data')]

a = Analysis(['PongHockey.py'],
             pathex=['/home/kone/PycharmProjects/PongHockey'],
             binaries= binary,
             datas= files,
             hiddenimports=[],
             hookspath=[],
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
          name='PongHockey',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PongHockey')
