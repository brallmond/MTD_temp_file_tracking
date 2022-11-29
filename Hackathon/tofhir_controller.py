import uhal 
import os
import logging
import time
import json
import sys
import copy
import filecmp
import glob
from shutil import copyfile
from collections import OrderedDict
import bitarray
from petsys_py_lib import config, tofhir2, bitarray_utils

from chip import Chip
    
class TOFHIR(Chip):
    def __init__(self, nlinks, logfile, verbose=True, neports=28, wait=0.01, configdir='configdir', outdir='outTOFHIR2'):
	if not os.path.exists(outdir): os.mkdir(outdir)
	Chip.__init__(self, logfile, verbose, configdir, outdir)
        
        # Reset of chip counters and buffers.
        self.resetTFHRbuf_addr_cnt = self.hw.getNode("Common_rst_TFHR_Frame_addr_cnt")
        self.reset(self.resetTFHRbuf_addr_cnt)
        self.reset_time_tagger     = self.hw.getNode("Common_rst_TFHR_TT_counter")
        self.reset(self.reset_time_tagger)
        
        self.neports = neports
        self.nlinks = nlinks
        self.wait = wait
        
        self.status_links = []
        self.txRAMs = []
        self.rxRAMs_status = []
        self.TxTrig_freqs = []
        self.TxResync_freqs = []
        self.Tx_Resync_CMDs = []
        self.Tx_Config_CMDs = []
        self.init_lnks_modules = []
        self.rxRAMs = [[],[]]
        self.RxTTs  = [[],[]]
        
        self.links_init()
  
        self.CCLink = 1 
        self.CCPort = 'FE1' 
        self.ChipID = 1 
	self.InMap_eports = self.configdir+'/'+'readout_map_tofhir2.json'
        self.outValIrefCalDAC = self.configdir+'/'+'values_iref_cal_DAC.json'
        self.regs_param = self.configdir+'/'+'regs_params.json'

	self.packetReg34 = ""
 

    def configBase(self, link, config_file):
        '''
        Configure TOFHIR.
        '''
	config_file = self.configdir + '/' + config_file

	#create backup for configuration file
        self.create_backup(config_file, refFile=str(self.configdir)+'/'+'config_tofhir_2x_ref.json', backupPath=str(self.configdir)+'/'+'backup', outBFile = 'config.json')

        if self.verbose: print ("Start configuration TOFHIR for {} link".format(link))
        logging.info('Start configuration TOFHIR2 for link %s',link)
        
        #Core logic RESET 
        #self.chip_reset(link, 6)
        
        #if self.verbose: print("-------------- Set ASIC GLOBAL COMMAND ------------")
        #logging.info('---------- Set ASIC GLOBAL COMMAND ------------')
        #self.config_reg(link, 'Chip_reg32', config_file)

        #Global Reset to all ASIC!
        self.chip_reset(link, 16)

        if self.verbose: print("-------------- Set configuration mode -------------")
        logging.info('---------- Set configuration mode -------------')
        self.config_reg(link, 'Chip_reg33', config_file)
 

    def config(self, link, channelList, config_file):
        '''
        Configure TOFHIR.
        '''
	config_file = self.configdir + '/' + config_file

	#create backup for configuration file
        self.create_backup(config_file, refFile=str(self.configdir)+'/'+'config_tofhir_2x_ref.json', backupPath=str(self.configdir)+'/'+'backup', outBFile = 'config.json')
     
        #Core logic RESET 
        self.chip_reset(link, 6)

        if self.verbose: print("-------------- Set ASIC GLOBAL COMMAND ------------")
        logging.info('---------- Set ASIC GLOBAL COMMAND ------------')   
        self.config_reg(link, 'Chip_reg32', config_file)
        
        #Core logic RESET 
        #self.chip_reset(link, 6)

        for i in channelList:
           if self.verbose: print "-------------- Set ASIC CHANNEL COMMAND (channel =",i,")------------"
           logging.info('---------- Set ASIC CHANNEL COMMAND (channel = %s)------------',i)
           self.config_reg(link, 'Chip_reg{:02d}'.format(int(i)), config_file)
           #Core logic RESET 
           self.chip_reset(link, 6)

        if self.verbose: print ("Configuration TOFHIR on {} link is finished".format(link))
        logging.info('Configuration TOFHIR on %s link is finished', link)
        
    def readout(self, map_file, out_file, ncyc_read):
        '''
        TOFHIR readout.
        '''
        logging.info('Start readout TOFHIR2')
        
        node = [self.Tx_Resync_CMDs[0], self.Tx_Resync_CMDs[1]]
        self.sync_reset(node)
        
        self.reset(self.resetTFHRbuf_addr_cnt)
        self.reset(self.reset_time_tagger)
        
        #load readout map with mapLink, enableLink, readMaskIni 
	map_file = self.configdir + '/' + map_file 
        with open(map_file) as json_file:
            data = json.load(json_file, object_pairs_hook=OrderedDict)

        self.mapLink = data['mapLink']
        self.enableLink = data['enableLink']
        self.readMaskIni = data['readMaskIni']

        MEM = []
        timeout, n_cycle = 0,0
        n_word = 1020 #512  1024   
        TTnWord = 255 #nWord / 4 
        channel_read = copy.deepcopy(self.enableLink)
        
	if self.verbose: print("File name: {}/{}".format(self.outdir, out_file))
        file = open(self.outdir+"/"+out_file, "w")
        file.write( "Link ID; Channel ID; Line; time tag; Data \n")       
 
        while n_cycle < int(ncyc_read) and timeout < 10000:
            for link in range(self.nlinks):
		for key in self.mapLink:
                    self.readFEB(key, self.rxRAMs_status[link], n_word, TTnWord, self.rxRAMs[link], 
                                 self.RxTTs[link], link, channel_read, file)
                
		if self.verbose: print(channel_read[str(link)].values())
                logging.info('%s',channel_read[str(link)].values())
                               
            if self.readMaskIni == channel_read: 
                n_cycle+=1
                               
                if self.verbose:
                    print("cycle: %d") % n_cycle
                    print("Total: %d") % ncyc_read
                               
                logging.info('cycle: %s',n_cycle)
                logging.info('Total: %s',ncyc_read)
                channel_read = copy.deepcopy(self.enableLink)
                if self.verbose: print(channel_read)
                               
                self.reset(self.resetTFHRbuf_addr_cnt)
                if self.verbose: print(channel_read)
                               
                timeout = 0
            timeout += 1
                               
        if self.verbose:
            print("")
            print("frequency frames with recognized headers")
            logging.info('frequency frames with recognized headers')
                    
        for link in range(self.nlinks):
            if self.verbose:
               print("link: ", link )
               print("frequency frames with recognized headers")
                               
            logging.info('link: %s',link) 
            logging.info('frequency frames with recognized headers')
            N_word = 27
            FREQ = []
	    time.sleep(0.3)           
            FREQ = self.status_links[link].readBlock(int(N_word))
            self.hw.dispatch()

            # print result
            for x in range(int(N_word)):
                if self.verbose: print("e-port {} {} Hz".format(x, FREQ[x]))
                logging.info('e-port %s   %s Hz', x, FREQ[x])
                               
    def readFEB(self, connectorID, TOFHIR_rxRAM_status, nWord, TTnWord, TOFHIR_RxBRAM, 
                TOFHIR_RxTT, linkID,  channelRead, file):
        '''
        Read FEB. 
        '''
        RAM_status = TOFHIR_rxRAM_status.read()
        self.hw.dispatch()
                               
        channelIDs  = self.mapLink[connectorID];
        channelMask = self.enableLink[str(linkID)][connectorID]
                               
        for index, channel in enumerate(channelIDs):
            if ((RAM_status>>channelIDs[index] & 0x1) == 1 and 
                channelMask[index] == 1 and 
                channelRead[str(linkID)][connectorID][index] == 1):
                               
                if self.verbose: print("----------- Read Rx answer e-port {}------------".format(channel))
                logging.info('----------- Read Rx answer e-port {}------------ %s',channel)
                               
                self.read_eport_wt_tag(channel, nWord, TTnWord, TOFHIR_RxBRAM[channel], 
                                       TOFHIR_RxTT[channel], linkID ,file)
                channelRead[str(linkID)][connectorID][index] = 0
        
    def readeport(self, ChID, n_word, TOFHIR_RxBRAMch, linkID, file):
        '''
        Read e-port.
        '''
        frame_data = 0
        MEM = []
        xx, yy = 1, 0
        
        MEM = TOFHIR_RxBRAMch.readBlock(int(n_word))
        self.hw.dispatch()
        
        for x in range(int(n_word)):
            if yy == 3:
                frame_data = frame_data + ((MEM[x]&0xFFFFFFFF)<<yy*32)
                yy = 0
                file.write( str("{:3d};{:3d};{:3d};".format(linkID, ChID, xx)+ hex(frame_data) + "\n"))
                xx = xx + 1
                frame_data = 0
            else :
                frame_data = frame_data + ((MEM[x]&0xFFFFFFFF)<<yy*32)
                
    def read_time_tag(self, ChID, n_word, TOFHIR_RxTTch, linkID, file):
        '''
        Read time tag.
        '''
        TTData = 0
        MEM = []
        xx, yy = 1, 0

        MEM=TOFHIR_RxTTch.readBlock(int(n_word*2));
        self.hw.dispatch();
        
        for x in range(int(n_word-1)):
            TTData = (MEM[x*2]&0xFFFFFFFF)+((MEM[x*2+1]&0xFFFFFFFF)<<32)
            file.write( str("{:3d};{:3d};{:3d};".format(linkID, ChID, xx)+ hex(TTData) + "\n"))
        
    def read_eport_wt_tag(self, ChID, n_word, tn_word, RxBRAMch, RxTTch, linkID, file):
        frame_data = 0
        port_MEM = []
        TTData = 0
        tMEM, tTag = [], []
        xx, yy = 1, 0
        
        port_MEM = RxBRAMch.readBlock(int(n_word))
        
        tMEM = RxTTch.readBlock(int(tn_word*2))
        self.hw.dispatch()

        for t in range(int(tn_word)):
            TTData = (tMEM[t*2]&0xFFFFFFFF)+((tMEM[t*2+1]&0xFFFFFFFF)<<32)
            tTag.append(hex(TTData))

        # print result
        for x in range(int(n_word)):
            if yy == 3:
                frame_data = frame_data + ((port_MEM[x]&0xFFFFFFFF)<<yy*32)
                yy = 0
                file.write( str("{:3d};{:3d};{:3d};".format(linkID, ChID, xx)+tTag[xx-1]+";"+hex(frame_data) + "\n"))
                xx += 1
                frame_data = 0
            else :
                frame_data = frame_data + ((port_MEM[x]&0xFFFFFFFF)<<yy*32)
                yy += 1

        
    def chip_reset(self, link, reslen):
        '''
        Reset chip.
        '''
        self.reset(self.reset_time_tagger)
        self.reset(self.resetTFHRbuf_addr_cnt)
        self.reset(self.TxResync_freqs[link], value=int(reslen))
        self.reset(self.Tx_Resync_CMDs[link])
 
        if reslen <=3:
            logging.info('Reset only time tag counter')
            if self.verbose:
                print("Reset only time tag counter")
        elif reslen >= 4 and reslen <= 7: 
            logging.info('Reset core logic')
            if self.verbose:
                print("Reset core logic")
        else:
            logging.info('Global reset')
            if self.verbose:
                print("Global reset")
        
    def set_reg_config(self, reg, link, config_file):
        '''
        Set configuration for specified register.
        '''
        
        if self.verbose: print("-------------- Set configuration for Reg{} -------------".format(reg))
        logging.info('---------- Set configuration for Reg %s  -------------', reg)
        self.config_reg(link, 'Chip_reg{}'.format(reg), config_file)
        
        self.chip_reset(link, 6)
                
    def links_init(self):
        '''
        Initialization of the links.
        '''
        for link in range(self.nlinks):
            self.status_links.append(self.hw.getNode("LINK"+str(link)+"_RHCnt_status"))
            self.txRAMs.append(self.hw.getNode("Tx"+str(link)+"BRAM"))
            self.rxRAMs_status.append(self.hw.getNode("Rx"+str(link)+"RAM_status"))
            self.TxTrig_freqs.append(self.hw.getNode("Tx"+str(link)+"_Trig_Freq"))
            self.TxResync_freqs.append(self.hw.getNode("Tx"+str(link)+"_Resync_Freq"))
            self.Tx_Resync_CMDs.append(self.hw.getNode("Tx"+str(link)+"_Resync_CMD"))
            self.Tx_Config_CMDs.append(self.hw.getNode("Tx"+str(link)+"_Config_CMD"))
            self.init_lnks_modules.append(self.hw.getNode("Init_TOFHIR_EC_IC_modules"+str(link)))

            self.TxTrig_freqs[link].write(0)
        
            # initialize TOFHIR, IC and EC moduls
            self.init_lnks_modules[link].write(1);
            self.hw.dispatch();
            time.sleep(0.5)
            
            for eport in range(self.neports):
                self.rxRAMs[link].append(self.hw.getNode("Rx"+str(link)+"BRAM_CH"+str(eport)))
                self.RxTTs[link].append(self.hw.getNode("Rx"+str(link)+"TT_CH"+str(eport)))
                
    def config_reg(self, link, packet, configFile):
        '''
        Configuration of registers.
        '''
        word_str = ["0x80"] + [""] * 8
        
        ############### Open JSON file for reading configuration ###################
        with open(configFile) as jsonFile:
            data = json.load(jsonFile, object_pairs_hook=OrderedDict)
            length = len(data)
            k=0
            for i in range(0, length):
                    for key, value in data[i].iteritems():
                            #print key
                            if key == packet: k=i
                                    
            #registers
            for key0, value0 in data[k][packet][0].iteritems():
                if int(data[k][packet][0]['R/W mode'])  == 1 and key0 == "Register address":
                    regx = int(value0, base=16)
                   ##replace bit 
                    regx |= 1 << 7
                    value0 = hex(regx).replace("0x","")
                if key0 != "CC link" and key0 != "CC port" and key0 != "R/W mode":
                    word_str[0] += str(value0)
		if key0 == "CC link":
		    self.CCLink = int(value0)	
		if key0 == "CC port":
		    self.CCPort = str(value0)	
		if key0 == "ChipID":
		    self.ChipID = int(value0)	

            for i in range(1,9):
                for key, value in data[k][packet][i].iteritems():
                    word_str[i] += str(value)

        ############### Open JSON file for reading map for eports ####################
	eport = 0 
	with open(self.InMap_eports) as jsonFile2:
            data_eport = json.load(jsonFile2, object_pairs_hook=OrderedDict)
            for i in range(0, len(data_eport['ChipID']['{}'.format(self.CCPort)])):
               if int(data_eport['ChipID']['{}'.format(self.CCPort)][i]) == int(self.ChipID):
		  eport = data_eport['mapLink']['{}'.format(self.CCPort)][i]   

        n_word = 10
        port_MEM = [0x0] * n_word

	''' 
        self.rxRAMs[link][eport].writeBlock(port_MEM)
        self.hw.dispatch()

        port_MEM = self.rxRAMs[link][eport].readBlock(int(n_word))
        self.hw.dispatch()
        
        if self.verbose: print ("Read rxRAM")
        logging.info('Read rxRAM')
        
        self.registers_log(verbose=self.verbose, n_word=n_word, portMEM=port_MEM, packet=packet)
        time.sleep(self.wait)
        '''  
        ############### Send configuration to ASICs  ##########
        if self.verbose: print ("Send  configuration: ")
        logging.info('Send  configuration:')
        
        ##----------- set Tx0RAM ------------
        n_word = 10 # data payload = 280 bits = 9x32bits words (8,75, 9 words without 1 LSB byte)
        cfg_value = [0x0] * n_word
        
        # set configuration data
        for i in range(9):
            cfg_value[i] = int(word_str[8-i], base=16)  #3,4-data 1,0-not used   
                                                        #3-80 2-chip ID 1-opcode+Register address 0-Register length  
        self.txRAMs[link].writeBlock(cfg_value);
        self.hw.dispatch();
	#time.sleep(self.wait)

        ##----------- Check TxRAM ------------
        #MEMs = []
        #MEMs=self.txRAMs[link].readBlock(int(n_word))
        #self.hw.dispatch()
 	#time.sleep(self.wait)
        
        # print result
	#self.registers_log(self.verbose, int(n_word-1), port_MEM, MEMs, str_name='payload', packet=packet)

        value = 1
        if self.verbose: print("send Config CMD")
        logging.info('send Config CMD')
    
        self.reset(self.Tx_Config_CMDs[link], int(value))
        time.sleep(self.wait)
        
        self.reset(self.resetTFHRbuf_addr_cnt)
        time.sleep(self.wait)

        port_MEM = self.rxRAMs[link][eport].readBlock(int(n_word));
        self.hw.dispatch()
        #time.sleep(self.wait)
        
        if self.verbose: print("Read rxRAM")
        logging.info('Read rxRAM')
        
	self.registers_log(verbose=self.verbose, n_word=n_word, portMEM=port_MEM, packet=packet)   
 
    def DAC_calib(self, link, config_file):
        '''
        DAC calibration. 
        '''
	config_file = self.configdir + '/' + config_file	
        if self.verbose: print ("Start TOFHIR DAC calibration for {} link".format(link))
        logging.info('Start TOFHIR2 DAC calibration for link %s', link)

        #Core logic RESET 
        self.chip_reset(link, 6)

        if self.verbose: print("-------------- Set ASIC GLOBAL COMMAND ------------")
        logging.info('---------- Set ASIC GLOBAL COMMAND ------------')
        self.config_reg(link, 'Chip_reg32', config_file)

        #Global Reset to all ASIC!
        self.chip_reset(link, 16)

        self.set_reg_config(35, link, config_file)
        self.set_reg_config(36, link, config_file)

        if self.verbose: print("---------------- Iref_probe_enable to 1 -----------------")
        logging.info('------------ Iref_probe_enable to 1 -----------------') 
	os.system("sed -i '/global.Iref_probe_enable = /c global.Iref_probe_enable = 1' "+str(self.configdir)+"/config_dac.ini")

        if self.verbose: print("---------------- Comparator_enable to 1 -----------------")
        logging.info('------------ Comparator_enable to 1 -----------------')
	os.system("sed -i '/global.Comparator_enable = /c global.Comparator_enable = 1' "+str(self.configdir)+"/config_dac.ini")

        statusReg34 = 0

        for i in range(0,256):
            if statusReg34 == 1: continue
            var = "0x{:02x}".format(i)

            if self.verbose: print "---------------- Iref_cal_DAC to ",i," (",var,")---------------------"
            logging.info('------------ Iref_cal_DAC to %s (%s) ---------------------',i,var)

	    os.system("sed -i '/global.Iref_cal_DAC = /c global.Iref_cal_DAC = "+str(i)+"' "+str(self.configdir)+"/config_dac.ini")
            self.json_builder('config_dac.ini', 'autogen.json', self.CCLink, self.CCPort, self.ChipID, [0], 0, 0, 0, 0, verbose=self.verbose)

            if self.verbose: print("-------------- Set ASIC GLOBAL COMMAND ------------")
            logging.info('---------- Set ASIC GLOBAL COMMAND ------------')
	    self.config_reg(link, 'Chip_reg32', str(self.configdir)+'/autogen.json')

            #Core logic RESET 
            self.chip_reset(link, 6)

            self.set_reg_config(34, link, config_file)
	
	    FEboardChipID = '00111100100000010000' + format(self.ChipID, '05b') + '1000000' 

	    if self.packetReg34.find(FEboardChipID) == -1:
                if self.verbose: print("Packet not found")
                logging.warning('Packet not found with status of Reg34')
	    else:
                if self.verbose: print("Packet is found for Reg34")
                logging.info('Packet is found for Reg34')
                statusReg34 = 1
		data = {"CC link": '{:02d}'.format(self.CCLink),
			"CC port": '{}'.format(self.CCPort),
			"ChipID": '{:02d}'.format(self.ChipID),
			"Iref_cal_DAC": '{:03d}'.format(i)
			}
		# Append JSON object with value iref_cal_DAC to output file JSON array
		if os.path.isfile(self.outValIrefCalDAC):
    		   #File exists
		   with open(self.outValIrefCalDAC, 'a+') as outfile:
        	       outfile.seek(-1, os.SEEK_END)
        	       outfile.truncate()
        	       outfile.write(',')
        	       json.dump(data, outfile, sort_keys=True, indent=4)
        	       outfile.write(']')
		else: 
    		   #Create file
    		   with open(self.outValIrefCalDAC, 'w') as outfile:
        	       array = []
        	       array.append(data)
                       json.dump(array, outfile, sort_keys=True, indent=4)

            	if self.verbose: print("Status DAC calibration is True")
                logging.info('Status DAC calibration is True')

            if i==255: 
   	    	if self.verbose: print("Status DAC calibration is False")
            	logging.info('Status DAC calibration is False')

            #Core logic RESET 
            self.chip_reset(link, 6)

        if self.verbose: print("TOFHIR DAC calibration on "+str(link)+" link is finished")
        logging.info('TOFHIR DAC calibration on %s link is finished', link)
    
        
    def registers_log(self, verbose, n_word, portMEM, MEMs=None, str_name=None, packet=None): 
        '''
        Logging info of register configuration. 
        '''
        self.packetReg34 = ""

        for x in range(int(n_word)):
            if str_name: 
                if x==8: str_name='header'
                if verbose:
                    print("addr={}, data={} {}".format(x, hex(MEMs[x]), str(str_name)))
                logging.info('addr = %s  data = %s   %s', x, hex(MEMs[x]), str(str_name))

            else:
                if verbose: print("addr={}, data={}".format(x, hex(portMEM[x])))
                logging.info('addr = %s  data = %s', x, hex(portMEM[x]))

		if packet == "Chip_reg34":
                    self.packetReg34 += format(portMEM[x], '032b')


    @staticmethod
    def portMapping(CCport):
        port_dict = {"FE1":3, "FE2":2, "FE3":3, "FE4":3, "FE5":4, "FE6":5, "FE7":3, "FE8":7, "FE9":8, "FE10":9, "FE11":10, "FE12":11}
        return int(port_dict[CCport])


    def json_builder(self, inFile, outFile, CCLink, CCPort, ChipID, channelList, ith_t1, ith_t2, ith_e, ov, verbose=True):
        inFile = str(self.configdir) + '/' + inFile
        outFile = str(self.configdir) + '/' + outFile

	#create backup for initial configuration
        self.create_backup(inFile, refFile=str(self.configdir)+'/'+'config_ref.ini', backupPath=str(self.configdir)+'/'+'backup')

	# ccLink, ccPort and chipID
        targetAsics = [ (CCLink, CCPort, ChipID) ]

        # Allocate  default ASIC configurations
        asicsConfig = {}
        for ccLink, ccPort, chipID in targetAsics:
            asicsConfig[(ccLink, ccPort, chipID)] = tofhir2.AsicConfig()

        # Apply configurations from config.ini
        # load configuration from file
        mask = config.LOAD_ALL
        mask ^= config.LOAD_QDCMODE_MAP
        mask ^= config.LOAD_BIAS_SETTINGS
        mask ^= config.LOAD_BIAS_CALIBRATION
        mask ^= config.LOAD_DISC_SETTINGS
        mask ^= config.LOAD_MAP
        systemConfig = config.ConfigFromFile(inFile, loadMask=mask)
        systemConfig.applyConfigToAsics(asicsConfig)

        # Modify the ASIC configurations as needed.
        # Example: For every ASIC, set the thresholds of a channel
        for (ccLink, ccPort, chipID), ac in asicsConfig.items():
            gc = ac.globalConfig
	    # Open JSON file for reading value Iref_cal_DAC  
            data_iref = []
	    if os.path.isfile(self.outValIrefCalDAC) and inFile != str(self.configdir)+'/'+'config_dac.ini':
               with open(self.outValIrefCalDAC) as jsonFile:
                   data_iref = json.load(jsonFile, object_pairs_hook=OrderedDict)
                   # set up value global.Iref_cal_DAC
                   length = len(data_iref)
                   #set default value
                   iref_cal_dac = 177
                   for i in range(0, length):
                      if data_iref[i]['CC link'] == '{:02d}'.format(ccLink) and data_iref[i]['CC port'] == '{}'.format(ccPort) and data_iref[i]['ChipID'] == '{:02d}'.format(chipID):
                         iref_cal_dac = data_iref[i]['Iref_cal_DAC']
                         print("iRef DAC on LINK%d PORT%s ASIC%d:  %d"%(int(ccLink),ccPort,int(chipID),int(iref_cal_dac)))
                   gc.setValue("Iref_cal_DAC", iref_cal_dac)
        '''  
            for aldoID in ['A', 'B']:
                bd, over__ = systemConfig.getBiasChannelDefaultSettingsAldo((ccLink, self.portMapping(ccPort), chipID, aldoID))
                dac = systemConfig.mapALDOVoltageToDAC((ccLink, self.portMapping(ccPort), chipID, aldoID), bd, float(ov), verbose)
                gc.setValue("Valdo_%s_DAC"%aldoID, dac)

            for channel in channelList:
                channel = int(channel)
                cc = ac.channelConfig[channel]

                if ith_t1 is not None:
                    dac_setting_ith1 = systemConfig.mapAsicChannelThresholdToDAC((ccLink, self.portMapping(ccPort), chipID, channel), "vth_t1", int(ith_t1))
                    cc.setValue("cfg_a3_ith_t1", dac_setting_ith1)
                if ith_t2 is not None:
                    dac_setting_ith2 = systemConfig.mapAsicChannelThresholdToDAC((ccLink, self.portMapping(ccPort), chipID, channel), "vth_t2", int(ith_t2))
                    cc.setValue("cfg_a3_ith_t2", dac_setting_ith2)
                if ith_e is not None:
                    dac_setting_ithe = systemConfig.mapAsicChannelThresholdToDAC((ccLink, self.portMapping(ccPort), chipID, channel), "vth_e", int(ith_e))
                    cc.setValue("cfg_a3_ith_e", dac_setting_ithe)
        '''

        self.write_json(asicsConfig, outFile)
        if self.verbose: print("---------------- Configuration file created from JsonBuilder -----------------")
        logging.info('------------ Configuration file created from JsonBuilder -----------------')


    def write_json(self, asicsConfig, outputFileName):

        outputFile = open(outputFileName, "w")

        targetAsics = asicsConfig.keys()
        targetAsics.sort()


        json_data = []

        for ccLink, ccPort, chipID in targetAsics:
                ac = asicsConfig[(ccLink, ccPort, chipID)]

                json_data.append(self.make_json_register(ccLink, ccPort, chipID, 32, ac.globalConfig))
                json_data.append(self.make_json_register(ccLink, ccPort, chipID, 33, ac.globalConfigTX))
                for ch in range(32):
                        json_data.append(self.make_json_register(ccLink, ccPort, chipID, ch, ac.channelConfig[ch]))
                json_data.append(self.make_json_register(ccLink, ccPort, chipID, 34, ac.globalConfigStatus))
                json_data.append(self.make_json_register(ccLink, ccPort, chipID, 35, ac.Register35))
                json_data.append(self.make_json_register(ccLink, ccPort, chipID, 36, ac.Register36))

        outputFile.write(json.dumps(json_data, sort_keys=True, indent=4))

        outputFile.close()
        return None

   
    def make_json_register(self, ccLink, ccPort, chipID, register_id, cfg_value):
        register_write = True

        register_length = len(cfg_value)
        payload = bitarray.bitarray(256)
        payload.setall(False)
        payload[0:register_length] = cfg_value[0:register_length]
        payload = bytearray(payload.tobytes())

        cmd32 = [0 for n in range(8)]
        for n, v in enumerate(payload):
                idx32 = n/4
                sh32 = 3 - (n % 4)
                sh32 *= 8

                v32 = cmd32[idx32]
                v32 = v32 | (v << sh32)
                cmd32[idx32] = v32

        json_data = []
        # Open JSON file for reading register_length
        with open(self.regs_param) as jsonFile:
           data_rl = json.load(jsonFile, object_pairs_hook=OrderedDict)
           length = len(data_rl)
           #print data_rl
           for i in range(0, length):
              if data_rl[i]['register_id'] == '{:d}'.format(register_id):
                 register_length = int(data_rl[i]['register_length'])
                 rw_mode = int(data_rl[i]['rw_mode'])
        json_data.append({
                "CC link" : "%02X" % ccLink,
                "CC port" : "%s" % ccPort,
                "ChipID" : "%02X" % chipID,
                "R/W mode" : "%d" % rw_mode,
                "Register address" : "%02X" % register_id,
                "Register length" : "%02X" % register_length

                })

        for idx32, v32 in enumerate(cmd32):
                rev32 = 7 - idx32
                json_data.append({ "dword%d" % rev32 : "%08X" % v32 })

        json_data = { "Chip_reg%02d" % (register_id) : json_data }

        return json_data

        return  None


    def create_backup(self, inFile, refFile = 'config_ref.ini', backupPath = 'backup', sizeBackup = 40, outBFile = 'config.ini'):
        comp = filecmp.cmp(inFile, refFile)
        if comp == False:
           if not os.path.exists(backupPath):
                os.mkdir(backupPath)
                if self.verbose: print ("Backup directory is created in {}".format(backupPath))
                logging.info('Backup directory is created in %s', backupPath)
	   dir_name = os.getcwd() + '/' + backupPath + '/'
           for i in range(sizeBackup):
	        list_of_files = filter(os.path.isfile, glob.glob(dir_name + '*'))
		list_of_files = sorted(list_of_files, key = os.path.getctime)	
                nfiles=0
                forDel = ''
                for key, elem in enumerate(list_of_files):
                    if key == 0:
                        forDel = elem
                    nfiles+=1
                if os.path.exists(dir_name + 'v'+str(i)+'_'+outBFile) and nfiles>=sizeBackup:
                   os.remove(forDel)
                if not os.path.exists(dir_name + 'v'+str(i)+'_'+outBFile):
                   copyfile(inFile, dir_name + 'v'+str(i)+'_'+outBFile)
                   if self.verbose: print("Backup file for config.ini is created for history")
                   logging.info('Backup file for config.ini is created for history')
                   break
