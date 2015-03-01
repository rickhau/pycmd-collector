#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: pycmdCollector.py
# Description: command line output log collection Tool
# This Tool is mainly to collect the command line output logs 
# on Windows and Linux platforms.
#
# Change History
# v0.0.3 Add docstring to every method
# v0.0.2 Add PyWin32 and Windows Event Log dump
# v0.0.1 Initial Release

# import modules
#from datetime import datetime
import subprocess
import os, sys
import logging
import zipfile
import time
import shutil
import csv
import logging

version = '0.0.3'
author = 'Rick Lin'
platform = sys.platform
if 'cygwin' == platform or 'win32' == platform:
    os_name = 'Win'
else:
    os_name = 'Linux'

logging_level = 'INFO'
LOGNAME       = 'logcollect.log'
LOGDIRNAME    = 'cmdoutput'
ZIPFILENAME   = 'cmdline_logs'
ZIPNAME       = ''
TIMEFORMAT    = '%Y-%m-%d-%H%M%S_'
LOGPATH       = os.path.join(os.getcwd(), LOGDIRNAME)
LOGLIST       = []
log           = logging.info
logfd         = sys.stdout


def createLogDir():
    """ This creates a log directory called 'cmdoutput' for log dump.
        The directory will be deleted after log archive.
    """

    global LOGPATH
    global LOGDIRNAME

    logging.debug("Entering createLogDir()")
    if os.path.exists(LOGPATH): # if any previous log exists, remove it
        shutil.rmtree(LOGPATH)
    os.mkdir(LOGDIRNAME) # create a new one
    os.chdir(LOGPATH)

    logging.debug("Switch to log directory: %s " % os.getcwd())
    logging.debug("Exit createLogDir()")
    return

def zipLogDir():
    """ This creates a zip to archive all logs in 'cmdoutput' directory
    """

    global ZIPNAME
    global TIMEFORMAT
    global LOGPATH

    now = time.localtime(time.time())
    date = time.strftime(TIMEFORMAT, now)
    ZIPNAME = date + ZIPFILENAME + '.zip'
    zipf = zipfile.ZipFile(ZIPNAME, 'w')
    for dirname, subdirs, files in os.walk(LOGPATH):
        for file in files:
            if file.endswith('log'):
                zipf.write(file)
    zipf.close()

    os.chdir('..') 
    updir = os.getcwd()
    shutil.move(os.path.join(LOGPATH, ZIPNAME), updir) # move zip file to parent directory
    logging.debug("%s archive is created at %s " % (ZIPNAME, updir))
    shutil.rmtree(LOGPATH)
    return

def getstatusoutput(cmd):
    """ This capture the output and status of the command execution.
        @cmd: individual command
        Return (status, output) of executing cmd in a shell.
    """

    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)  
    output = "".join(pipe.stdout.readlines()) 
    sts = pipe.returncode
    if sts is None: 
        sts = 0
    return sts, output  

def runCommands(cmd, outfile):
    """ This executes commands and writes the command output to file, which is to do the log dump
        @cmd: individual command
        @outfile: the filename of log dump
    """
    
    global LOGLIST
    logging.debug("Entering runCommands()")
    (status, output) = getstatusoutput(cmd)
    if status == 0:
        f = open(outfile, "w")
        log("Dumping (%s) to %s " % (cmd, outfile))
        f.write(cmd + "\n")
        f.write("----------\n")
        f.write(output)
        LOGLIST.append(outfile)  # remember how many files are dumpped
        f.close()
    else:
        log("[%s] command error!" % cmd)
        logging.debug("Exit runCommands()")
    return

def openCommand(cmdfile):
    """ This parses the command recipe and run it line by line
        @cmdfile: command receipe
    """
    try:
        with open(cmdfile, 'rb') as f:
            lines = csv.reader(f)
            for line in lines:
                if line == []:
                    continue
                runCommands(line[0].strip(), line[1].strip()) # strip() is to remove spaces
    except IndexError as e:
        log("[{}]: Incorrect csv format for parsing!, {}".format(os.path.basename(cmdfile), e))
        shutil.rmtree(os.path.dirname(os.getcwd()))
        sys.exit()
    except(csv.Error, IOError, ValueError) as e:
        log("Error: {}".format(e))
        shutil.rmtree(os.path.dirname(os.getcwd()))
        sys.exit()

def init(mode=logging_level, logname=LOGNAME):
    """ This method is to set up the log dump configuration
        Default is to write the message to sys.stdout and message only format
        If you set the level to "DEBUG", it will write to the log file(logname) in detail message format
        @mode: "INFO" or "DEBUG"
        @logname: default="logcollect.log"
    """
    global logging_level
    global LOGNAME
    global logfd

    if mode == 'DEBUG':
        logging_level = mode
        LOGNAME = logname
        fmt = "%(module)s.%(funcName)s |%(asctime)-15s|(PID: %(process)d)|%(levelname)s|%(message)s"
        if os.path.exists(logname):
            os.remove(logname)
        logfd = open(logname, "w")
    else:
        logging_level = mode
        fmt = "%(message)s"
        logfd = sys.stdout
    logging.basicConfig(level=mode, stream=logfd, format=fmt)


def main():
    '''This main fuction reads the command recipe, runs it and archives the log dump into zip file
    '''
    global log
    global logfd    

    init() # Initialize the logging setup configuration

    print "COMMAND LINE LOG COLLECTION TOOL"
    print "Author: {0} / VERSION: {1} ".format(author, version)
    print "----------------------------------"

    if len(sys.argv) != 2:
        print "<command list file> is required"
        print "Usage: {} <command list file>".format(sys.argv[0])
        print "command list file format: "
        print "   command1, output1.log"
        print "   command2, output2.log"
        print "   ..., ..."
        return
    else:
        print "Input command file: [{}]".format(sys.argv[1])
        cmdlistfile = os.path.abspath(sys.argv[1])

    # Redirect the log output from logging.info to logging.debug
    if logging_level == "DEBUG":
        log = logging.debug
        print "VERBOSE is set to ON"
    
    ### Dump Windows Event Log ###
    if os_name == 'Win':
        try:
            import pyWinEvt
        except ImportError as e:
            log("ERROR: {}".format(e))
            log("Unable to enable Windows Event Log Dump")
            log("{} exit...".format(sys.argv[0]))
            raise SystemExit
    ### Dump Windows Event Log ###

    createLogDir()

    ### Dump Windows Event Log ###
    if os_name == 'Win':
        server = 'localhost'
        logTypes = ["System", "Application", "Security"]
        log("Dumping Windows System Event Log...")
        pyWinEvt.getAllEvents(server, logTypes, LOGPATH)
    ### Dump Windows Event Log ###

    openCommand(cmdlistfile)
    zipLogDir()

    log("\nLog dump arcive is located at [{}]".format(os.path.abspath(ZIPNAME)))

    if 'DEBUG' == logging_level:
        logfd.close()

if __name__ == "__main__":
    main()
