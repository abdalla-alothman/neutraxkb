#!/bin/bash
if [ $(id -u) != 0 ]
then
    echo "root privileges required"
    exit 1
fi
if [ ! -d /usr/share/neutraxkb ] 
then
  mkdir /usr/share/neutraxkb
  if [ ! -d /usr/share/neutraxkb/wolrd-flags ]
  then
    tar xvfJ flagIcons.tar.xz -C /usr/share/neutraxkb/
  fi
else
    echo "directory exists."
    exit 1 
fi
env python3 setup.py install
