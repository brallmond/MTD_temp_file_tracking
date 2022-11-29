import logging
import argparse
import emp
import time 
import uhal 
from chip import Chip
from sca_enum import *

class sca_com(Chip):
"""
Class providing SCA communication
"""
    #def ic_write(self, addr, values, gbtx_addr):
    #    value = self.emp_cont.getSCCIC().icWriteBlock(addr, values, gbtx_addr)
    #    print("from ic_write in sca_com")
    #    print(value)

    #def ic_read(self, addr, gbtx_addr):
    #    value = self.emp_cont.getSCCIC().icRead(addr, gbtx_addr)
    #    print("from ic_read in sca_com")
    #    print(value) 
        
class sca_cont():
"""
Class providing functions for SCA control.
"""    
    def __init__(self, path, fpga, link):
        """
        Initializing sca_cont class enables a hw_interface thru the sca_com class
        """
        self.sca_com = sca_com()
        self.sca_com.hw_interface(path, fpga, link)
        self.l = link

    def connect(self, sca_addr): 
        self.sca_com.emp_cont.getDatapath().selectLink(self.l)
        self.sca_com.emp_cont.getSCC().reset()
        self.sca_com.emp_cont.getSCCEC().sendConnectCommand(sca_addr)

    def create_payload(self, ch, leng, com, data):
        addr_offset = int('0x000000ff', 16)
        tx_com = ((addr_offset & int(com, 16)) << 16)
        tx_leng = ((addr_offset &  int(leng, 16)) << 8)
        tx_ch = (addr_offset &  int(ch, 16))

        tx_p1 = tx_com + tx_leng + tx_ch

        c_txpayloads = [tx_p1, int(data,16)]

        print("Sent commands: ")
        print("tx_chan : tx_len : tx_com : tx_data")
        print('{} : {} : {} : {}'.format(hex(tx_ch), hex(tx_leng), hex(tx_com), data))
        #print(hex(c_txpayloads))
        print(' ')
        return c_txpayloads

    def send_command(self, ch, leng, com, data, sca_addr, reset_SCCEC_flag):

        tx_p1 = self.create_payload(ch, leng, com, data)

        # reset SCC
        self.sca_com.emp_cont.getDatapath().selectLink(self.l)
        self.sca_com.emp_cont.getSCC().reset()
        ver = '2.1'
        
        # reset SCCEC
        if (reset_SCCEC_flag):
          ack = self.sca_com.emp_cont.getSCCEC().sendResetCommand(int(sca_addr, 16), ver)
          print('GBT-SCA reset acknowledged: {}'.format(ack))
          time.sleep(0.5)
        
        # send commands to SCA and receive replies
        c_rxpayloads = self.sca_com.emp_cont.getSCCEC().sendCommandsAndReceiveReplies(tx_p1, int(sca_addr, 16), ver)
        print('rxpayloads: ', hex(c_rxpayloads[0]), hex(c_rxpayloads[1]))
        rx_chan  = (int('0x0000ff00', 16) & c_rxpayloads[0]) >> 8    # truncatse 2 bits
        rx_len   = (int('0x00ff0000', 16) & c_rxpayloads[0]) >> 16   # truncates 4 bits
        rx_error = (int('0xff000000', 16) & c_rxpayloads[0]) >> 24   # truncates 6 bits
        rx_data  = c_rxpayloads[1]

        print("Replies: ")
        print("rx_chan : rx_len : rx_com : rx_data")
        print('{} : {} : {} : {}'.format(hex(rx_chan), hex(rx_len), hex(rx_error), hex(rx_data)))
        return c_rxpayloads



class sca_chip(sca_cont):

    def __init__(self, path, fpga, link, sca_addr="0x0000"):
        super(sca_chip, self).__init__(path, fpga, link)
        self.sca_addr = sca_addr
        self.regs_read = { "CRB" : SCA_Register.CTRL_R_CRB,
                           "CRC" : SCA_Register.CTRL_R_CRC,
                           "CRD" : SCA_Register.CTRL_R_CRD,
                           "SEU" : SCA_Register.CTRL_R_SEU,
                         }

        self.regs_write = { "CRB" : SCA_Register.CTRL_W_CRB,
                            "CRC" : SCA_Register.CTRL_W_CRC,
                            "CRD" : SCA_Register.CTRL_W_CRD,
                            "SEU" : SCA_Register.CTRL_C_SEU,
                          }

        self.I2C_channels = {"CTRL" : 0x00, # SCA configuration registers
                            "SPI" : 0x01, # SPI
                            "GPIO" : 0x02, # Parallel_IO_interface
                            "I2C0" : 0x03, # I2C Serial interface – master 0
                            "I2C1" : 0x04, # I2C Serial interface – master 1
                            "I2C2" : 0x05, # I2C Serial interface – master 2
                            "I2C3" : 0x06, # I2C Serial interface – master 3
                            "I2C4" : 0x07, # I2C Serial interface – master 4
                            "I2C5" : 0x08, # I2C Serial interface – master 5
                            "I2C6" : 0x09, # I2C Serial interface – master 6
                            "I2C7" : 0x0A, # I2C Serial interface – master 7
                            "I2C8" : 0x0B, # I2C Serial interface – master 8
                            "I2C9" : 0x0C, # I2C Serial interface – master 9
                            "I2CA" : 0x0D, # I2C Serial interface – master 10
                            "I2CB" : 0x0E, # I2C Serial interface – master 11
                            "I2CC" : 0x0F, # I2C Serial interface – master 12
                            "I2CD" : 0x10, # I2C Serial interface – master 13
                            "I2CE" : 0x11, # I2C Serial interface – master 14
                            "I2CF" : 0x12
                            }


        self.channels = {0 : ["CRB", CRBBits.ENI2C0.value],
                         1 : ["CRB", CRBBits.ENI2C1.value],
                         2 : ["CRB", CRBBits.ENI2C2.value],
                         3 : ["CRB", CRBBits.ENI2C3.value],
                         4 : ["CRB", CRBBits.ENI2C4.value],
                         5 : ["CRC", CRCBits.ENI2C5.value], 
                         6 : ["CRC", CRCBits.ENI2C6.value], 
                         7 : ["CRC", CRCBits.ENI2C7.value], 
                         8 : ["CRC", CRCBits.ENI2C8.value], 
                         9 : ["CRC", CRCBits.ENI2C9.value], 
                         10 : ["CRC", CRCBits.ENI2CA.value], 
                         11 : ["CRC", CRCBits.ENI2CB.value], 
                         12 : ["CRC", CRCBits.ENI2CC.value], 
                         13 : ["CRD", CRDBits.ENI2CD.value],
                         14 : ["CRD", CRDBits.ENI2CE.value],
                         15 : ["CRD", CRDBits.ENI2CF.value],
                        }

        self.freqs = { "100kHz": 0b00,
                       "200kHz": 0b01,
                       "400kHz": 0b10,
                       "1MHz"  : 0b11,
                     }

        self.nbyteshex = 0x04
        self.freqbin = 0b10

    def set_freq(self, freq):
        self.freqbin = self.freqs[freq]
        

    def set_nbytes(self, nbytes):
        if (nbytes >= 16 or nbytes < 1): raise "data out of bounds"
        self.nbyteshex = hex(nbytes)
        
    def write_i2c(self, I2C_channel, value):
        reg  = SCA_Register.I2C_W_CTRL
        ch   = hex(self.I2C_channels[f"I2C{I2C_channel}"])
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        data = hex( (0 | (self.nbyteshex << 2) | self.freqbin) << reg.value.Offset)
        #print("from write_i2c ", reg, ch, leng, com, data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)

        reg  = SCA_Register.I2C_R_CTRL
        ch   = hex(self.I2C_channels[f"I2C{I2C_channel}"])
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        self.send_command(ch, leng, com, hex(0), self.sca_addr, 0)


#    def read_i2c(self, I2C_channel, init=False): 
#        if init: 
#            self.init_i2c(I2C_channel)

    def init_i2c(self, I2C_channel): 
        print(self.channels[I2C_channel])
        reg = self.channels[I2C_channel][0]
        mask = 1 << self.channels[I2C_channel][1]
        print('mask: ', mask)
        self.mask_control_regs(reg, mask=mask)
        
    def mask_control_regs(self, Reg_ID, mask):
        rxpayloads = self.read_control_regs(Reg_ID)
        payload = rxpayloads[1] >> self.regs_read[Reg_ID].value.Offset
        payload = payload | mask
        payload = payload << self.regs_write[Reg_ID].value.Offset
        print('offset: ', hex(self.regs_write[Reg_ID].value.Offset))
        print('payload: ', hex(payload))
        self.write_control_regs(Reg_ID, payload) 
    
    def write_control_regs(self, Reg_ID, value): # set default ch = 0 ? 
        reg = self.regs_write[Reg_ID]
        ch   = hex(reg.value.Channel) #hex(0)
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        print('write com: ', com)
        data = hex(value)
        print('write data: ', data)
        print('rxpayloads from write_control_regs: ', ch, leng, com, data) 
        rxpayloads = self.send_command(ch, leng, com, data, self.sca_addr, 0)
        return rxpayloads

    def read_control_regs(self, Reg_ID):
        
        reg = self.regs_read[Reg_ID]
        ch   = hex(reg.value.Channel) #hex(0)
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        print('read com: ', com)
        data = hex(reg.value.Data)
        print('read data: ', data) 

        rxpayloads = self.send_command(ch, leng, com, data, self.sca_addr, 0)
        return rxpayloads


    def reset_SEU(self):
        ch   = hex(SCA_Register.CTRL_C_SEU.value.Channel.value) 
        leng = hex(SCA_Register.CTRL_C_SEU.value.Length)
        com  = hex(SCA_Register.CTRL_C_SEU.value.CMD)
        data = hex(SCA_Register.CTRL_C_SEU.value.Data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)


    def get_ID(self):
        ch   = hex(SCA_Register.CTRL_R_ID.value.Channel.value)
        leng = hex(SCA_Register.CTRL_R_ID.value.Length)
        com  = hex(SCA_Register.CTRL_R_ID.value.CMD)
        data = hex(SCA_Register.CTRL_R_ID.value.Data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)


# get a logger for lpGBT library logging
#sca_logger = logging.getLogger("sca")
    
