#!/bin/sh

rm -rf dist/*
python setup.py sdist
python setup.py bdist

cd dist
FILE=`ls radiotray-*.*.linux-i686.tar.gz`
cd ..

mkdir -p tmp/debian
cp -r DEBIAN tmp/debian
cp dist/$FILE tmp/debian
cd tmp/debian
tar zxvf $FILE
rm $FILE 
cd ..
dpkg-deb --build debian
mv debian.deb ../dist/radiotray_x.x_all.deb
cd ..
rm -rf tmp
