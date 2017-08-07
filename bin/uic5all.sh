#!/usr/bin/env bash
# Converts .ui in .py
pyuic5 mainwindow.ui -o ../fume/ui/mainwindow.py;
pyuic5 settings.ui -o ../fume/ui/settings.py;
pyuic5 log.ui -o ../fume/ui/log.py;
pyuic5 filter.ui -o ../fume/ui/filter.py;
pyuic5 about.ui -o ../fume/ui/about.py;
