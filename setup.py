'''
    QBI Batch Crop: setup.py (Windows 64bit MSI)
    *******************************************************************************
    Copyright (C) 2017  QBI Software, The University of Queensland

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''
#
# Step 1. Build first
#   python setup.py build
# View build dir contents
# Step 2. Create MSI distribution (Windows)
#   python setup.py bdist_msi
# View dist dir contents
####
# Issues with scipy and cx-freeze -> https://stackoverflow.com/questions/32432887/cx-freeze-importerror-no-module-named-scipy
# 1. changed cx_Freeze/hooks.py scipy.lib to scipy._lib (line 560)
# then run setup.py build
# 2. changed scipy/spatial cKDTree.cp35-win_amd64.pyd to ckdtree.cp35-win_amd64.pyd
# 3. change Plot.pyc to plot.pyc in multiprocessing
# test with exe
# then run bdist_msi
# create 64bit from 32bit python with python setup.py build --plat-name=win-amd64
# NB To add Shortcut working dir - change cx_freeze/windist.py Line 61 : last None - > 'TARGETDIR'
import os
import shutil
import sys
from os.path import join

from cx_Freeze import setup, Executable

from autoanalysis.App import __version__

application_title = 'QBI Batch SlideCropper'
main_python_file = join('autoanalysis','App.py')
venvpython = join(sys.prefix,'Lib','site-packages')
mainpython = "D:\\Programs\\Python36"

os.environ['TCL_LIBRARY'] = join(mainpython, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = join(mainpython, 'tcl', 'tk8.6')
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'
ufuncs_version='_ufuncs.cp36-win_amd64.pyd' #'_ufuncs.cp36-win32.pyd'
build_exe_options = {
    'includes': ['idna.idnadata', "numpy", "h5py","packaging.version","packaging.specifiers", "packaging.requirements","appdirs",'scipy.spatial.cKDTree'],
    'excludes': ['PyQt4', 'PyQt5'],
    'packages': ['wx','sqlite3','scipy', 'numpy.core._methods', 'numpy.lib.format','matplotlib','matplotlib.backends.backend_agg','skimage'],
    'include_files': ['autoanalysis/',join(mainpython, 'DLLs', 'sqlite3.dll'),
                      (join(venvpython, 'scipy', 'special', ufuncs_version), '_ufuncs.pyd')],
    'include_msvcr': 1

}
bdist_msi_options = {
    "upgrade_code": "{175FE673-CF61-416B-9C82-EF811886165D}" #get uid from first installation regedit
    }
# MSDAnalysis HKEY_USERS\S-1-5-21-2111889174-1506992555-1484156688-1004\Software\Microsoft\Windows\CurrentVersion\Search\RecentApps\{8077FF32-9BEE-4769-9630-736FB8A49026}

setup(
    name=application_title,
    version=__version__,
    description='Crops image of slides (IMS) into individual TIFF images',
    long_description=open('README.md').read(),
    author='Liz Cooper-Williams, QBI',
    author_email='e.cooperwilliams@uq.edu.au',
    maintainer='QBI Custom Software, UQ',
    maintainer_email='qbi-dev-admin@uq.edu.au',
    url='http://github.com/QBI-Microscopy/BatchCrop',
    license='GNU General Public License (GPL)',
    options={'build_exe': build_exe_options, 'bdist_msi': bdist_msi_options},
    executables=[Executable(main_python_file,
                            base=base,
                            targetName='batchcrop.exe',
                            icon='autoanalysis/resources/app.ico',
                            shortcutName=application_title,
                            shortcutDir='DesktopFolder'
                            )]
)

#Rename ckdtree
os_version='exe.win-amd64-3.6' #'exe.win32-3.6'
ckd_version= 'cKDTree.cp36-win_amd64.pyd' #'cKDTree.cp36-win32.pyd'
shutil.move(join('build',os_version,'lib','scipy','spatial',ckd_version), join('build',os_version,'lib','scipy','spatial','ckdtree.pyd'))
shutil.copyfile(join('build',os_version,'lib','scipy','spatial','ckdtree.pyd'), join('build',os_version,'lib','scipy','spatial',ckd_version))
