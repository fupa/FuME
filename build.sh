#!/bin/sh -e
#
# This script simplyfies building process for FuME on MacOS. For more details please see usage
#
#

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"

usage() {
	cat <<EOF
Usage:
$(basename "$0") [-h] [-b -c -r]

Description:
Builds the FuME.app with PyInstaller which is located in 'dist' directory.

Optional switches:
  -b, --build-dmg
    Builds a .dmg with the new FuME.app.

  -c, --clean-up
    Removes 'dist' and 'build' directory if exist.

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

build_app() {
    msg_status "Building FuME.app with PyInstaller"
    pyinstaller -y --log-level=WARN main.spec
    msg_status "Finished building"
}

build_dmg() {
    msg_status "Building FuME.dmg in 'dist'"
    cd dist
    dmgbuild -s ../dmgbuild.py -D app=FuME.app "FuME" FuME.dmg
    cd ..
    msg_status "Finished building .dmg"
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
        -b|--build-dmg)
        dmg=true
        ;;
        -c|--cleanup)
        cleanup=true
        ;;
        -r|--reset)
        reset=true
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

build_app

if [ "$dmg" = true ]; then
    build_dmg
fi