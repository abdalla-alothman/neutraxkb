#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(name='neutraxkb',
    version='1.0',
    author='Abdalla S. A. Alothman',
    author_email='abdallah.alothman@gmail.com',
    license='GPL',
    description='NeutraXkbSwitch is a system tray tool to switch between user defined keyboard layouts. The tool requires any panel with a system tray enabled. It further requires PyQt4.',
    py_modules=['neutraxkbconfig', 'nxkbcfgparser', 'XkbConfig_rc', 'XkbConfig_ui'],
    scripts = ['neutraswitch', 'neutrakb.py'],
    )
