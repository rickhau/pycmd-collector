#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: pycmdCollector.py
# Description: command line output log collection Tool
# This Tool is mainly to collect the command line output logs 
# on Windows and Linux platforms.
#
# Change History
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

version = '0.0.2'
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


def createLogDir(DIR=LOGDIRNAME):
    logging.debug("Entering createLogDir()")
    if os.path.exists(LOGPATH): # if any previous log exists, remove it
        shutil.rmtree(LOGPATH)
    os.mkdir(DIR) # create a new one
    os.chdir(LOGPATH)

    logging.debug("Switch to log directory: %s " % os.getcwd())
    logging.debug("Exit createLogDir()")
    return

def zipLogDir(path=LOGPATH):
    global ZIPNAME
    now = time.localtime(time.time())
    date = time.strftime(TIMEFORMAT, now)
    ZIPNAME = date + ZIPFILENAME + '.zip'
    zipf = zipfile.ZipFile(ZIPNAME, 'w')
    for dirname, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith('log'):
                zipf.write(file)
    zipf.close()

    #curdir = os.getcwd()
    os.chdir('..')
    updir = os.getcwd()
    shutil.move(os.path.join(LOGPATH, ZIPNAME), updir)
    return

def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell."""
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)  
    output = "".join(pipe.stdout.readlines()) 
    sts = pipe.returncode
    if sts is None: 
        sts = 0
    return sts, output  

def runCommands(cmd, outfile):
    global LOGLIST
    logging.debug("Entering runCommands()")
    (status, output) = getstatusoutput(cmd)
    if status == 0:
        f = open(outfile, "w")
        logging.info("Dumping (%s) to %s " % (cmd, outfile))
        f.write(cmd + "\n")
        f.write("----------\n")
        f.write(output)
        LOGLIST.append(outfile)  # remember how many files are dumpped
        f.close()
    else:
        logging.info("[%s] command error!" % cmd)
        logging.debug("Exit runCommands()")
    return

def rmLogs(path=LOGPATH):
    global LOGLIST
    for dirname, subdirs, files in os.walk(path):
        for file in files:
            if file in LOGLIST:
                os.remove(os.path.join(dirname, file))
                LOGLIST.remove(file)
    #logging.info("current dir: %s " % (os.getcwd()))
    if os.path.basename(os.getcwd()) == LOGDIRNAME:
        parentdir = os.path.dirname(os.getcwd())
        os.chdir(parentdir)
    shutil.rmtree(os.path.join(os.getcwd(), LOGDIRNAME))
    return

def openCommand(cmdfile):
    try:
        with open(cmdfile, 'r') as f:
            lines = csv.reader(f)
            for line in lines:
                if line == []:
                    continue
                runCommands(line[0].strip(), line[1].strip()) # strip() is to remove spaces
    except IndexError as e:
        logging.info("[{}]: Incorrect csv format for parsing!, {}".format(os.path.basename(cmdfile), e))
        rmLogs(os.path.dirname(os.getcwd()))
        sys.exit()
    except(csv.Error, IOError, ValueError) as e:
        logging.info("Error: {}".format(e))
        rmLogs(os.path.dirname(os.getcwd()))
        sys.exit()


def main():
    '''function document
    logging module practice
    '''
    formatter = "%(module)s.%(funcName)s |%(asctime)-15s|(PID: %(process)d)|%(levelname)s|%(message)s"

    if 'DEBUG' == logging_level:
        f = open(LOGNAME, "w")
        logging.basicConfig(level=logging.DEBUG, stream=f, format=formatter)
    else:
        #logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="|%(asctime)-15s|%(message)s")
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")

    logging.info("COMMAND LINE LOG COLLECTION TOOL")
    logging.info("Author: {0} / VERSION: {1} ".format(author, version))
    logging.info("----------------------------------")

    if len(sys.argv) != 2:
        logging.info("<command list file> is required")
        logging.info("Usage: {} <command list file>".format(sys.argv[0]))
        logging.info("command list file format: ")
        logging.info("   command1, output1.log")
        logging.info("   command2, output2.log")
        logging.info("   ..., ...")
        return
    else:
        logging.info("Input command file: [{}]".format(sys.argv[1]))
        cmdlistfile = os.path.abspath(sys.argv[1])
    
    ### Dump Windows Event Log ###
    if os_name == 'Win':
        try:
            import pyWinEvt
        except ImportError as e:
            logging.info("ERROR: {}".format(e))
            logging.info("Unable to enable Windows Event Log Dump")
            logging.info("{} exit...".format(sys.argv[0]))
            raise SystemExit
    ### Dump Windows Event Log ###

    createLogDir(LOGDIRNAME)

    ### Dump Windows Event Log ###
    if os_name == 'Win':
        server = 'localhost'
        logTypes = ["System", "Application", "Security"]
        logging.info("Dumping Windows System Event Log...")
        pyWinEvt.getAllEvents(server, logTypes, LOGPATH)
    ### Dump Windows Event Log ###

    openCommand(cmdlistfile)
    zipLogDir(LOGPATH)
    rmLogs(LOGPATH)

    logging.info("\nLog dump arcive is located at [{}]".format(os.path.abspath(ZIPNAME)))

    if 'DEBUG' == logging_level:
        f.close()

if __name__ == "__main__":
    main()
