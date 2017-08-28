#!/bin/sh -e
#
# --------------------------------------------------------------------------
# FuME FuPa Match Explorer Copyright (c) 2017 Andreas Feldl <fume@afeldl.de>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The full license of the GNU General Public License is in the file LICENCE,
# distributed with this software; if not, see http://www.gnu.org/licenses/.
# --------------------------------------------------------------------------
#
# This script simplyfies building process for FuME on MacOS. For more details please see usage
#
#

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"

usage() {
	cat <<EOF
Usage:
$(basename "$0") [-h] [-c -d -e -r]

Description:
Builds FuME with PyInstaller which is located in 'dist' directory.

Optional switches:
  -c, --clean-up
    Removes 'dist' and 'build' directory if existing.

  -d, --build-dmg
    Builds a .dmg with the new FuME.app.

  -e, --build-exe
    Builds an Installer for Windows

  -r, --reset
    Removes Application Support files (e.g. database) and FuMEs setting files, useful for developing

EOF
}

msg_status() {
	echo "\033[0;32m-- $1\033[0m"
}
msg_error() {
	echo "\033[0;31m-- $1\033[0m"
}

build() {
    msg_status "Building FuME with PyInstaller"
    pyinstaller -y --log-level=WARN main.spec
    msg_status "Finished building"
}

build_dmg() {
    msg_status "Building FuME.dmg in 'dist'"
    cd dist
    /usr/local/bin/dmgbuild -s ../build_dmg.py "FuME" FuME.dmg
    cd ..
    msg_status "Finished building .dmg"
}

build_exe() {
    msg_status "Building FuME.exe in 'dist'"
    "C:\Program Files (x86)\Inno Setup 5\ISCC" build_exe.iss
    msg_status "Finished building .exe"
}

cleanup() {
    msg_status "Removing 'dist' and 'build'"
    if [ ! -e "dist" ]; then
        msg_error "dist folder not found, continue anyway..."
    else
        rm -rf dist
    fi
    if [ ! -e "build" ]; then
        msg_error "build folder not found, continue anyway..."
    else
        rm -rf build
    fi
    msg_status "Finished cleanup"
}

reset() {
    msg_status "Removing Application Support files and settings for $(whoami)"
    rm -rf "/Users/$(whoami)/Library/Application Support/FuME"
    rm "/Users/$(whoami)/Library/Preferences/com.fume.Match-Explorer.plist"
    msg_status "Finished reset"
}

while [[ $# -gt 0 ]]; do
    key="$1"
    case ${key} in
        -d|--build-dmg)
        dmg=true
        ;;
        -c|--cleanup)
        cleanup=true
        ;;
        -r|--reset)
        reset=true
        ;;
        -e|--build-exe)
        exe=true
        ;;
        -h|-?|--help)
        usage
        exit 1
        ;;
        *)
        msg_error "Unknown options"
        usage
        exit 1
        ;;
    esac
    shift
done

if [ "$cleanup" = true ]; then
    cleanup
elif [ "$reset" = true ]; then
    reset
fi

build

if [ "$dmg" = true ]; then
    build_dmg
elif [ "$exe" = true ]; then
    build_exe
fi