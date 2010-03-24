#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, string
from RadioTray import RadioTray

current_path = os.path.realpath(__file__)
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "radiotray.py")):
    if os.path.exists(os.path.join(os.getcwd(), "radiotray.py")):
        basedir = os.getcwd()
sys.path.insert(0, basedir)
os.chdir(basedir)

def main():
    RadioTray()

if __name__ == "__main__":
    main()
