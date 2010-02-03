#!/usr/bin/env python

from distutils.core import setup


setup(name='radiotray',
      version='0.3',
      author='Carlos Ribeiro',
      author_email='carlosmribeiro1@gmail.com',
      url='http://radiotray.sourceforge.net',
      description='Radio Tray is an online radio stream player',
      license='GPL',
      packages=['radiotraylib'],
      data_files=[('share/radiotray',['configBookmarks.glade','COPYING','README','NEWS']), ('share/radiotray/icons',['icons/radiotray.png']), ('share/applications',['radiotray.desktop'])],
      scripts=['radiotray']
     )
