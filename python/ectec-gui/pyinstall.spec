#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The specifications to package `ectec-gui` with pyinstaller.

***********************************

Created on 2021/10/11 at 17:43:57

Copyright (C) 2021 real-yfprojects (github.com user)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
from pathlib import Path

# Spec

block_cipher = None

# EctecGui Server
analysis_a = Analysis(['server-entry.py'],
                      pathex=['.'],
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
pyz_a = PYZ(analysis_a.pure, analysis_a.zipped_data, cipher=block_cipher)
exe_a = EXE(pyz_a,
            analysis_a.scripts, [],
            exclude_binaries=True,
            name='ectecgui-server',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True)

# EctecGui Client
analysis_b = Analysis(['client-entry.py'],
                      pathex=["."],
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
pyz_b = PYZ(analysis_b.pure, analysis_b.zipped_data, cipher=block_cipher)
exe_b = EXE(pyz_b,
            analysis_b.scripts, [],
            exclude_binaries=True,
            name='ectecgui-client',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True)

# Collect
coll = COLLECT(exe_a,
               analysis_a.binaries,
               analysis_a.zipfiles,
               analysis_a.datas,
               exe_b,
               analysis_b.binaries,
               analysis_b.zipfiles,
               analysis_b.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ectecgui')
