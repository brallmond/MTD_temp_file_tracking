import uhal 
import os
import logging
import time
import emp
#################not used by class directly
#import json
#import sys
#import copy
#import filecmp
#import glob
#from shutil import copyfile
#from collections import OrderedDict
#import bitarray
#from petsys_py_lib import config, tofhir2, bitarray_utils


class Chip:
    def __init__(self, verbose=True, configdir='', outdir=''):
        self.configdir = configdir
        self.outdir = outdir
        self.verbose = verbose
        #self.logfile = logfile
        # Hardware interface
        #self.hw = self.hw_interface(filepath="file://"+self.configdir+"/"+"Real_connections.xml", verbose=self.verbose, logfile=self.logfile, outdir=self.outdir)

    def configBase(self):
        pass

    def config(self):
        pass

    def DAC_calib(self):
        pass

    def readout(self):
        pass

    def json_builder(self):
        pass

    def reset(self, node, value=1):
        '''
        Reset a node.
        '''
        node.write(value)
        self.hw.dispatch()

    def sync_reset(self, node, value=2):
        '''
        Synchronized reset. 
        '''
        for n in node:
            n.write(value)
        self.hw.dispatch()

    @staticmethod
    def hw_interface_kcu105(device="KCU105real", filepath="file://Real_connections.xml",
                     verbose=True, logfile="outlog.log", outdir=''):
        '''
        Creates hardware interface.
        '''
        uhal.disableLogging()
        connectionMgr = uhal.ConnectionManager(filepath)
        hw = connectionMgr.getDevice(device)

        if os.path.exists(outdir+'/'+logfile):
            if verbose:
                size = os.path.getsize(outdir+'/'+logfile)
                print('logfile size is ', size)
                if size > 10000*1024: os.remove(outdir+'/'+logfile)

        logging.basicConfig(filename=outdir+'/'+logfile, format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        logging.info('Started chip initialization...')

        return hw

    def hw_interface(self, path, fpga, link):
        self.con_man = uhal.ConnectionManager("file://"+path) #xml file for the ipbus communication 
        self.hw_int  = uhal.HwInterface(self.con_man.getDevice(fpga))
        self.emp_cont = emp.Controller(self.hw_int)
        self.emp_cont.getDatapath().selectLink(link)
        self.emp_cont.getSCC().reset()
 


