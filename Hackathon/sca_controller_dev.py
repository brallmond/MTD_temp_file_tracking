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
        Initializing the sca_cont class sets up a hw_interface connection through the sca_com class
        """
        self.sca_com = sca_com()
        self.sca_com.hw_interface(path, fpga, link)
        self.l = link

    def connect(self, sca_addr):
        """ 
        To be tested
        Checks which port of the SCA is in use
        """
        self.sca_com.emp_cont.getDatapath().selectLink(self.l)
        self.sca_com.emp_cont.getSCC().reset()
        self.sca_com.emp_cont.getSCCEC().sendConnectCommand(sca_addr)

    def create_payload(self, ch, leng, com, data):
        """
        Concatenates the com, leng, and ch inputs and data to a single payload (a list with two entries)
        The list is returned by the function
        """
        # all registers have channel, command, and length info
        # so we can pass the register to this function instead of the ch, leng, com
        # data should be left separate
        addr_offset = int('0x000000ff', 16)
        tx_com  = ((addr_offset & int(com, 16)) << 16)
        tx_leng = ((addr_offset & int(leng, 16)) << 8)
        tx_ch   =  (addr_offset & int(ch, 16))

        tx_p1 = tx_com + tx_leng + tx_ch

        c_txpayloads = [tx_p1, int(data, 16)]

        print("Sent commands: ")
        print("tx_chan : tx_len : tx_com : tx_data")
        print('{} : {} : {} : {}'.format(hex(tx_ch), hex(tx_leng), hex(tx_com), data))
        #print(hex(c_txpayloads[0]), hex(c_txpayloads[1]))
        print(' ')
        return c_txpayloads

    def send_command(self, ch, leng, com, data, sca_addr, reset_SCCEC_flag):
        """
        Uses inputs to create a payload, send to SCA, and receive a reply from SCA.
        A flag determining whether the SCA is reset is also sent. Probably move to dedicated reset function :)
        """
        tx_p1 = self.create_payload(ch, leng, com, data)

        # reset SCC
        self.sca_com.emp_cont.getDatapath().selectLink(self.l)
        self.sca_com.emp_cont.getSCC().reset()
        ver = '2.1'

# break this part into a separate function
# to be tested
# def reset_SCCEC(self):
#     ack = self.sca_com.emp_cont.getSCCEC().sendResetCommand(int(sca_addr, 16), ver)
#     print('GBT-SCA reset acknowledged: {}'.format(ack))
#     time.sleep(0.5)
        
        # reset SCCEC
        if (reset_SCCEC_flag):
          ack = self.sca_com.emp_cont.getSCCEC().sendResetCommand(int(sca_addr, 16), ver)
          print('GBT-SCA reset acknowledged: {}'.format(ack))
          time.sleep(0.5)
        
        # send commands to SCA and receive replies
        c_rxpayloads = self.sca_com.emp_cont.getSCCEC().sendCommandsAndReceiveReplies(tx_p1, int(sca_addr, 16), ver)
        print('rxpayloads: ', hex(c_rxpayloads[0]), hex(c_rxpayloads[1]))
        rx_chan  = (int('0x0000ff00', 16) & c_rxpayloads[0]) >> 8    # truncates 2 bits
        rx_len   = (int('0x00ff0000', 16) & c_rxpayloads[0]) >> 16   # truncates 4 bits
        rx_error = (int('0xff000000', 16) & c_rxpayloads[0]) >> 24   # truncates 6 bits
        rx_data  = c_rxpayloads[1]

        print("Replies: ")
        print("rx_chan : rx_len : rx_com : rx_data")
        print('{} : {} : {} : {}'.format(hex(rx_chan), hex(rx_len), hex(rx_error), hex(rx_data)))
        return c_rxpayloads



class sca_chip(sca_cont):
"""
The sca_chip classes uses functions from the sca_cont class to provide a high level abstraction of 
common user operations, without the need for explicit chip architecture knowledge. 
"""

    def __init__(self, path, fpga, link, sca_addr="0x0000"):
        """
        Initializing the sca_chip class with the "super" command allows it to directly use functions from the
        sca_cont class, such as send_command. Multiple dictionaries are also defined for use in later functions.  
        """
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
        # I2C0 can be equivalently accessed/used with 
        # hex(sca_enum.channel_id("put some string")) # implemented later Thursday afternoon
        self.I2C_channels = {"CTRL" : 0x00, # SCA configuration registers
                            "SPI" : 0x01,  # SPI
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


        # more meaningful names would be ENI2C0 and the like,
        # or I2C_ch_1 to 15
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

        # frequency = data transfer rates
        self.freqs = { "100kHz": 0b00,
                       "200kHz": 0b01,
                       "400kHz": 0b10,
                       "1MHz"  : 0b11,
                     }

        self.nbyteshex = 0x04
        self.freqbin = 0b10

    def set_freq(self, freq):
        """
        Convert a user setting to a binary setting
        """
        self.freqbin = self.freqs[freq]

    def set_nbytes(self, nbytes):
        """
        Convert a user setting (integer number of bytes) to hexadecimal number of bytes
        """
        if (nbytes >= 16 or nbytes < 1): raise "data out of bounds, nbytes > 16 or < 1"
        self.nbyteshex = hex(nbytes)

    def write_i2c_7bit(self, I2C_channel, nbytes, freq, data_to_write, location_to_write):
        # Set nbytes and freq 
        #set_i2c_CTRL(self, I2C_channel, nbytes, freq)
        # set data
        #set_i2c_DATA(self, nbytes, array_data_bytes) 
        # execute command
        #reg  = SCA_Register.I2C_M_7B_W.value
        #ch   = reg.Channel
        #leng = reg.Length
        #com  = reg.CMD
        # could i use this format as the read_i2c_7bit? maybe
        #data = location_to_write << reg.Offset 
        #self.send_command(ch, leng, com, data, self.sca_addr, 0)
        #self.send_command(reg.Channel, reg.Length, reg.CMD, data, self.sca_addr, 0)
        pass

    def read_i2c_7bit(self, I2C_channel, nbytes, freq, location_to_read):
        # set nbytes and freq
        #set_i2c_CTRL(self, I2C_channel, nbytes, freq)
        # execute command
        #reg   = SCA_Register.I2C_M_7B_R.value
        #data  = location_to_read << reg.Offset
        #self.send_command(reg, data)
        # print registers # can be used with read or write I2C regs
        #view_i2c_DATA(self, nbytes, readwrite='read')
        pass

    def view_i2c_DATA(self, nbytes, readwrite):
        """
        Print out data from I2C DATA registers.
        This function can be used to view data in the I2C R (READ) DATA registers
        or to view data that the user uploaded to the I2C W (WRITE) DATA registers
        """
        # read nbyte registers of I2C_R_DATA0123
        #I2C_R_DATA0 has BYTE 12,13,14,15
        #I2C_R_DATA1 has BYTE 8 ,9 ,10,11
        #I2C_R_DATA2 has BYTE 4 ,5 ,6 ,7
        #I2C_R_DATA3 has BYTE 1 ,2 ,3 ,4
        #for byte in range(nbytes):

    def set_i2c_DATA(self, nbytes: int, array_data_bytes: list):
        """
        Set data in the I2C_W_DATA registers
        This function can only be used for writing, so the I2C_R_DATA registers are not treated.
        """
      # assert nbytes == len(array_data_bytes), 'nbytes must equal len(array_data_bytes)'
      #add to sca_enum.py
      #class I2CWriteDataBytes(IntEnum):
      # """
      # I2C Channel Write Data Offsets
      # """
      #BYTE0 = 24
      #BYTE1 = 16
      #BYTE2 = 8
      #BYTE3 = 0
      #BYTE4 = 24
      #BYTE5 = 16
      #BYTE6 = 8
      #BYTE7 = 0
      #BYTE8 = 24
      #BYTE9 = 16
      #BYTE10 = 8
      #BYTE11 = 0
      #BYTE12 = 24
      #BYTE13 = 16
      #BYTE14 = 8
      #BYTE15 = 0
        #reg_data_packet = 0
        #for byte in range(nbytes):
          #enum_byte = f'BYTE{byte}'
          #offset = I2CWriteDataBytes.BYTE{byte}.value
          #offset = I2CWriteDataBytes.enum_byte.value
          #if 0 <= byte < 4:
          #    reg = SCA_Register.I2C_W_Data0.value 
          #elif 4  <= byte < 8:
          #    reg = SCA_Register.I2C_W_Data1.value
          #elif 8  <= byte < 12:
          #    reg = SCA_Register.I2C_W_Data2.value
          #elif 12 <= byte < 16:
          #    reg = SCA_Register.I2C_W_Data3.value
          #reg_data_packet += array_data_bytes[byte] << offset

          # if we move to a new register, send the previous data_packet and reset it
          #if byte != 0 and byte % 4 == 0: 
          #    send_command(reg, reg_data_packet)
          #    reg_data_packet = 0
          # if its the final byte and the register has not been sent, send the register
          #elif (byte == nbytes - 1):
          #    send_command(reg, reg_data_packet)
          #    reg_data_packet = 0
        pass
        
    # rename to "set_i2c_CTRL"
    def write_i2c(self, I2C_channel, nbytes, freq):#value): #change i2c -> I2C
        """
        writes the frequency and nbytes of data to the control register of the I2C connection
        --> implies this function is either misnamed or unfinished (I2C has 4 registers to be written).
        """
        # TODO: can add .value to end of reg instead of calling each time
        reg  = SCA_Register.I2C_W_CTRL
        # should be available in sca_enums
        # hex(sca_enum.channel_id("put some string")) # implemented later Thursday afternoon
        ch   = hex(self.I2C_channels[f"I2C{I2C_channel}"])
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        #data = hex( (0 | (self.nbyteshex << 2) | self.freqbin) << reg.value.Offset)
        data = hex( (0 | (set_nbytes(nbytes) << 2) | set_freq(freq)) << reg.value.Offset)
        #print("from write_i2c ", reg, ch, leng, com, data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)

        # originally a test to determine if we could read the i2c, test again before removing :)
        #reg  = SCA_Register.I2C_R_CTRL
        #ch   = hex(self.I2C_channels[f"I2C{I2C_channel}"])
        #leng = hex(reg.value.Length)
        #com  = hex(reg.value.CMD)
        #self.send_command(ch, leng, com, hex(0), self.sca_addr, 0)


#    def read_i2c(self, I2C_channel, init=False): 
#        if init: 
#            self.init_i2c(I2C_channel)
#        reg  = SCA_Register.I2C_R_CTRL
#        ch   = hex(self.I2C_channels[f"I2C{I2C_channel}"])
#        leng = hex(reg.value.Length)
#        com  = hex(reg.value.CMD)
                                           #set zero data as default in send_command
#        self.send_command(ch, leng, com, hex(0), self.sca_addr, 0)


    def init_i2c(self, I2C_channel):
        """
        Enables the mapped channel in the `channels` dictionary
        """
        print(self.channels[I2C_channel])
        reg = self.channels[I2C_channel][0]
        mask = 1 << self.channels[I2C_channel][1]
        print('mask: ', mask)
        self.mask_control_regs(reg, mask=mask) 
        
    def mask_control_regs(self, Reg_ID, mask):
        """
        Applies a given mask to the payload (removes and reapplies the offset before writing)
        Could be written as (TODO: check) 
        payload = rxpayloads[1] | (mask << self.regs_read[Reg_ID].value.Offset)
        """
        rxpayloads = self.read_control_regs(Reg_ID)
        payload = rxpayloads[1] >> self.regs_read[Reg_ID].value.Offset
        payload = payload | mask
        payload = payload << self.regs_write[Reg_ID].value.Offset
        print('offset: ', hex(self.regs_write[Reg_ID].value.Offset))
        print('payload: ', hex(payload))
        self.write_control_regs(Reg_ID, payload) 
    
    def write_control_regs(self, Reg_ID, value):
        """
        Lowest level write register function
        "control" in the name refers to the GBT-SCA controller part of the SCA
        """
        reg = self.regs_write[Reg_ID]
        ch   = hex(reg.value.Channel)
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        print('write com: ', com)
        data = hex(value)
        print('write data: ', data)
        print('rxpayloads from write_control_regs: ', ch, leng, com, data) 
        rxpayloads = self.send_command(ch, leng, com, data, self.sca_addr, 0)
        return rxpayloads

    def read_control_regs(self, Reg_ID):
        """
        Lowest level read register function
        """
        reg = self.regs_read[Reg_ID]
        ch   = hex(reg.value.Channel)
        leng = hex(reg.value.Length)
        com  = hex(reg.value.CMD)
        print('read com: ', com)
        data = hex(reg.value.Data)
        print('read data: ', data) 

        rxpayloads = self.send_command(ch, leng, com, data, self.sca_addr, 0)
        return rxpayloads


    def reset_SEU(self):
        """
        Reset the Single Event Upset (SEU) counter register
        """
        ch   = hex(SCA_Register.CTRL_C_SEU.value.Channel.value) 
        leng = hex(SCA_Register.CTRL_C_SEU.value.Length)
        com  = hex(SCA_Register.CTRL_C_SEU.value.CMD)
        data = hex(SCA_Register.CTRL_C_SEU.value.Data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)
        #self.send_command(SCA_Register.CTRL_C_SEU.value)


    def get_ID(self):
        """
        Get SCA ID, should return 0x46ed, which is an ID unique to our GBT-SCA chip
        """
        ch   = hex(SCA_Register.CTRL_R_ID.value.Channel.value)
        leng = hex(SCA_Register.CTRL_R_ID.value.Length)
        com  = hex(SCA_Register.CTRL_R_ID.value.CMD)
        data = hex(SCA_Register.CTRL_R_ID.value.Data)
        self.send_command(ch, leng, com, data, self.sca_addr, 0)


#sca_logger = logging.getLogger("sca")
    
