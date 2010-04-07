#!/usr/bin/env python

from distutils.core import setup
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.dist import Distribution
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import info
import glob
import os
import sys
import subprocess
import platform

from src.lib.common import APPNAME, APPVERSION

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

class RadioTrayDist(Distribution):
  global_options = Distribution.global_options + [
    ("without-gettext", None, "Don't build/install gettext .mo files")]

  def __init__ (self, *args):
    self.without_gettext = False
    Distribution.__init__(self, *args)

class BuildData(build):
  def run (self):
    build.run (self)

    if self.distribution.without_gettext:
      return

    for po in glob.glob (os.path.join (PO_DIR, '*.po')):
      lang = os.path.basename(po[:-3])
      mo = os.path.join(MO_DIR, lang, 'radiotray.mo')

      directory = os.path.dirname(mo)
      if not os.path.exists(directory):
        info('creating %s' % directory)
        os.makedirs(directory)

      if newer(po, mo):
        info('compiling %s -> %s' % (po, mo))
        try:
          rc = subprocess.call(['msgfmt', '-o', mo, po])
          if rc != 0:
            raise Warning, "msgfmt returned %d" % rc
        except Exception, e:
          print "Building gettext files failed.  Try setup.py --without-gettext [build|install]"
          print "%s: %s" % (type(e), e)
          sys.exit(1)
class InstallData(install_data):
  def run (self):
    self.data_files.extend (self._find_mo_files ())
    install_data.run (self)


  def _find_mo_files (self):
    data_files = []

    if not self.distribution.without_gettext:
      for mo in glob.glob (os.path.join (MO_DIR, '*', 'radiotray.mo')):
       lang = os.path.basename(os.path.dirname(mo))
       dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
       data_files.append((dest, [mo]))

    return data_files


if platform.system() == 'FreeBSD':
  man_dir = 'man'
else:
  man_dir = 'share/man'


setup(name='radiotray',
    version=APPVERSION,
    author='Carlos Ribeiro',
    author_email='carlosmribeiro1@gmail.com',
    url='http://radiotray.sourceforge.net',
    description='Radio Tray is an online radio stream player',
    license='GPL',
    scripts=['radiotray'],
    data_files = [
      ('share/applications', glob.glob('data/images/*.png')),
      ('share/applications', glob.glob('data/*.desktop')),
      ('share/doc/radiotray-%s' % APPVERSION,
          ['AUTHORS', 'CONTRIBUTORS', 'COPYING', 'NEWS', 'README']),
      ('share/radiotray/images', glob.glob('data/images/*.png')),
      ('share/pixmaps', glob.glob('data/images/*.png')),
      ('share/radiotray', ['data/configBookmarks.glade', 'data/bookmarks.xml']),
    ],
    package_dir={'radiotray': 'src'},
    packages = ['radiotray', 'radiotray.lib'],
    cmdclass={'build': BuildData, 'install_data': InstallData,},
    distclass=RadioTrayDist,
 )
