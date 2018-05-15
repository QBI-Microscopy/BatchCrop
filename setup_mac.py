'''
    QBI Auto Analysis APP: setup_mac.py (Mac OSX package)
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

Usage:
    python setup_mac.py py2app --matplotlib-backends='-'


Notes:
    Clean on reruns:
    > rm -rf build dist __pycache__
    May need to use system python rather than virtualenv
    > /Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6 setup_mac.py py2app --matplotlib-backends='-' > build.log

    Macholib version=1.7 required to prevent endless recursions
    Specify matplotlib backends with '-'
'''
import sys
from os.path import join
from os import getcwd
#Self -bootstrapping https://py2app.readthedocs.io
# import ez_setup
# ez_setup.use_setuptools()

from setuptools import setup

from App import __version__

application_title = 'QBI AutoAnalysis SynapticVesicles'
exe_name='autoanalysis_sv'
#main_python_file = join('.','App.py')
#venvpython = join(sys.prefix,'Lib','site-packages')
#mainpython = "/Library/Frameworks/Python.framework/Versions/3.6/bin/python3"

# Add info to MacOSX plist
# plist = Plist.fromFile('Info.plist')
plist = dict(
    CFBundleName=exe_name,
    CFBundleDisplayName=application_title,
    NSHumanReadableCopyright='Copyright (c) 2018 Queensland Brain Institute',
    CFBundleTypeIconFile='newplot.icns',
    CFBundleVersion=__version__
            )

APP = ['App.py']
DATA_FILES = [join('autoanalysis','resources')]
PARENTDIR= join(getcwd(),'.')
OPTIONS = {'argv_emulation': True,
           #'use_pythonpath': True,
           'plist': plist,
           'iconfile': join('autoanalysis','resources','newplot.icns'),
           'packages': ['sqlite3','scipy', 'wx','pandas','autoanalysis.processmodules'],
           'includes':['six','appdirs','packaging','packaging.version','packaging.specifiers','packaging.requirements','os','numbers','future_builtins'],
           'bdist_base': join(PARENTDIR, 'build'),
           'dist_dir': join(PARENTDIR, 'dist'),
           }

setup(
    name=exe_name,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app','pyobjc-framework-Cocoa','numpy','scipy'],
)
