#!/bin/bash
# Thanks to the following link:
# http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html
# Description:
#   This script is to bundle the python scripts into one standalone executable file

if [[ -e pycmdLogger ]]; then
    rm -f pycmdLogger
fi

mkdir pycmd
cp pycmdCollector.py pycmd/__main__.py
cp pyWinEvt.py pycmd/
cd pycmd
zip -r ../pycmd2.zip *.*
cd ..
echo '#!/usr/bin/env python' | cat - pycmd2.zip > pycmdLogger
chmod +x pycmdLogger
rm -rf pycmd
rm -f pycmd2.zip
