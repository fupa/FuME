#!/bin/bash
FILES=/Users/Andreas/Documents/projects/unsign/FuME.app/Contents/*

#for f in $FILES; do
for f in `find /Users/Andreas/Documents/projects/FuME/dist/FuME`; do
    #echo "$f"
    if [ -f "$f" ]; then
        #echo "unsign $f"
        ./unsign "$f"
    fi
done