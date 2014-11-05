#!/bin/bash
# Thanks to the following link:
# http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html
# Description:
#   This script is to bundle the python scripts into one standalone executable file

if [[ -e pycmd-logger ]]; then
    rm -f pycmd-logger
fi

mkdir pycmd
cp pycmd-collector.py pycmd/__main__.py
cd pycmd
zip -r ../pycmd2.zip *.*
cd ..
echo '#!/usr/bin/env python' | cat - pycmd2.zip > pycmd-logger
chmod +x pycmd-logger
rm -rf pycmd
rm -f pycmd2.zip
