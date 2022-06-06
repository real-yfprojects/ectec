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
import sys
from pathlib import Path

# Spec

archive = True  # compression saves space
console = True
block_cipher = None

# Analysis
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
                      noarchive=not archive)

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
                      noarchive=not archive)

# # Merge
# MERGE((analysis_b, 'client-entry', 'ectecgui-client'),
#       (analysis_a, 'server-entry', 'ectecgui-server'))

# EctecGui Server
pyz_a = PYZ(analysis_a.pure, analysis_a.zipped_data, cipher=block_cipher)
exe_a = EXE(pyz_a,
            analysis_a.scripts, [],
            exclude_binaries=True,
            name='ectecgui-server',
            icon='res/ectec-icon/EctecIcon.ico',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=console)

# EctecGui Client
pyz_b = PYZ(analysis_b.pure, analysis_b.zipped_data, cipher=block_cipher)
exe_b = EXE(pyz_b,
            analysis_b.scripts, [],
            exclude_binaries=True,
            name='ectecgui-client',
            icon='res/ectec-icon/EctecIcon.ico',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=console)

# Collect
extra_data = [('README.md', '../../README.md', 'DATA'),
              ('EctecIcon.svg', 'res/EctecIcon.svg', 'DATA'),
              ('LICENSE', 'LICENSE', 'DATA')]
coll = COLLECT(exe_a,
               analysis_a.binaries,
               analysis_a.zipfiles,
               analysis_a.datas,
               exe_b,
               analysis_b.binaries,
               analysis_b.zipfiles,
               analysis_b.datas,
               extra_data,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Ectec')

if sys.platform == 'darwin':
    app_a = BUNDLE(exe_a,
                   name='ectec-server.app',
                   icon='res/ectec-icon/EctecIcon.png',
                   bundle_identifier=None)

    app_b = BUNDLE(exe_b,
                   name='ectec-client.app',
                   icon='res/ectec-icon/EctecIcon.png',
                   bundle_identifier=None)
