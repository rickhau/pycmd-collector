pycmd-collector
===============

pycmd-collector is a command line utility to dump all command line output to log files for further analysis.
It requires a command list receipe to feed in this tool.

...code-block:: bash
Usage: pycmd-collector <command recipe>


<command list recipe format>: Use ',' to separate the {command} and {logfile}
command1, logname1
command2, logname2
...,...

Ex:
ls -l, ls.log
myapp -A1 -t -s -a0, myapp0.log

...code-block:: bash
$ python pycmd-collector.py linuxcmd.txt
COMMAND LINE LOG COLLECTION OOL
Author: Rick Lin / VERSION: 0.0.1
----------------------------------
Input command file: [linuxcmd.txt]
Dumping (dmesg) to dmesg.log
Dumping (time) to time.log
Dumping (ls -l) to ls.log
$

It will generate a zip with all above command list.
Ex: 2014-11-05-130344_cmdline_logs.zip

OR

Standalone mode:

...code-block:: bash
$ ./pycmd-logger linuxcmd.txt

v0.0.1
~~~~~~
1. Supports Windows and Linux log dump
2. Tests on Windows 7 and RHEL6.3 x86-64
3. Package.sh is a shell script to bundle the python script into one standalone file

