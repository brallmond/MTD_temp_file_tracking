import random # For randint
import sys # For sys.argv and sys.exit
import uhal
import time
from sca_enum import *

class sca_cont():
#Class providing functions for SCA control.
    def __init__(self, var):
        #Initializing the sca_cont class with a dummy variable
        self.var = var


    def print_tx_payload(self, ch, leng, com, data):
        # print input command
        print("\t--Sent (tx)")
        print("\t ch : leng : com : data")
        print(f"\t {hex(ch)} : {hex(leng)} : {hex(com)} : {hex(data)}")

        #below prints exactly what is sent by Tx in the send_command function
        #tx_payload = (int(com) & 0xff) << 24 | (int(leng) & 0xff) << 16 | (int(ch) & 0xff) << 8 | (int(com) & 0xff)
        #print(f"\t tx_payload: {tx_payload}")


    def print_rx_payload(self, rxpayload):
        # print output from command
        assert len(rxpayload) == 2, f"rxpayload size must equal 2, it is {len(rxpayload)}"
        header = rxpayload[0]
        data   = rxpayload[1]
        err  = (header & (0xff << 24)) >> 24
        leng = (header & (0xff << 16)) >> 16
        ch   = (header & (0xff << 8))  >> 8
        com  = header &  0xff
        print("\t--Received (rx)") 
        print("\t err : leng : ch : Tr.ID : data")
        print(f"\t {hex(err)} : {hex(leng)} : {hex(ch)} : {hex(com)} : {hex(data)}")

        #below prints exactly what is checked by Rx loop in the send_command function
        #print(f"\t rx_payload header: {hex(header)}")
        #print(f"\t rx_payload data: {hex(data)}")


    def send_command(self, ch, leng, com, data, sca_addr, reset_SCCEC_flag):
    
        uhal.disableLogging()
    
        #connectionFilePath = "Real_connections.xml"
        connectionFilePath = "../../Real_connections.xml" #../Real_connections1.xml
        deviceId = "KCU105real"
    
        # PART 2: Creating the HwInterface
        connectionMgr = uhal.ConnectionManager("file://" + connectionFilePath)
        hw = connectionMgr.getDevice(deviceId)
    
        Init_EC_IC_moduls   = hw.getNode("A2")
    
        EC_Tx_Elink_Header  = hw.getNode("EC_Tx_Elink_Header")
        EC_Tx_SCA_Header 	= hw.getNode("EC_Tx_SCA_Header")
        EC_Tx_SCA_Data 	= hw.getNode("EC_Tx_SCA_Data")
        SCA_Rst_CMD 	= hw.getNode("SCA_Rst_CMD")
        SCA_Connect_CMD 	= hw.getNode("SCA_Connect_CMD")
        SCA_Test_CMD 	= hw.getNode("SCA_Test_CMD")
        SCA_Start_CMD 	= hw.getNode("SCA_Start_CMD")
        nFRAME          = hw.getNode("nFRAME")
    
        #EC_Rx_Elink_Header = hw.getNode("ECTxElinkHRAM")
        EC_Rx_SCA_Header = hw.getNode("EC_Rx_SCA_Header")
        EC_Rx_SCA_Data = hw.getNode("EC_Rx_SCA_Data")
    
        wait = .005
        # initialize IC and EC moduls
        TxValue = 1  
        Init_EC_IC_moduls.write(int(TxValue)) 
        hw.dispatch()
    
        # EOF register for SCA
        TxValue = 0 
        nFRAME.write(int(TxValue)) 
        hw.dispatch()
    
        if reset_SCCEC_flag == 1:
            TxValue = 0x00000000  # Address field
            EC_Tx_Elink_Header.write(int(TxValue)); 
            hw.dispatch();
            TxValue = 1;
            SCA_Connect_CMD.write(int(TxValue)); 
            hw.dispatch();
        trcount = 1
        retrycount = 0
        RxValue = 0
    
        ##### sending the command starts here, before establishes the connection to the SCA
    
        TxValue = (int(com) & 0xff) << 24 | (int(leng) & 0xff) << 16 | (int(ch) & 0xff) << 8 | (int(com) & 0xff)
    
        EC_Tx_SCA_Header.write(int(TxValue)) 
        hw.dispatch()
        TxValue = data  # data field

        # prints sent payload
        self.print_tx_payload(ch, leng, com, data)
    
        EC_Tx_SCA_Data.write(int(TxValue)) 
        hw.dispatch()
    
        SCA_Start_CMD.write(int(TxValue)) 
        hw.dispatch()
        RxValue = 0
        time.sleep(.1)
        RxValue = EC_Rx_SCA_Header.read()
        hw.dispatch()
        checkValue = ((int(ch) & 0xff) << 8) | (int(com) & 0xff)
        #print("header ", hex(RxValue))
        #checkValue = (0x2 << 16) | (int(ch) & 0xff << 8) | (int(com) & 0xff)
        #print("checkValue ", hex(checkValue))
        while RxValue & 0xffff != (checkValue) and retrycount < 20:    
            # read SCA results from RxRAM
            RxValue = EC_Rx_SCA_Header.read()
            hw.dispatch()
            retrycount += 1
        if retrycount >= 20: print("limit retry count")
        rxPayload = []
        rxPayload.append(int(RxValue))
        RxValue = EC_Rx_SCA_Data.read()
        hw.dispatch()
        #print("data ", hex(RxValue))
        rxPayload.append(int(RxValue))

        self.print_rx_payload(rxPayload)
        return(rxPayload)
    

class sca_chip(sca_cont):
# class to abstract chip functions
    
    sca_addr = 0

    def __init__(self):
        self.dummy_sca_chip = sca_cont(5)

    
    def send_reset(self):
        # non-functioning, should be in sca_cont anyways
        print("send reset!")
        reg = SCA_Register.CTRL_R_ID.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 1)


    def set_frequency(self, user_frequency):
        return Frequency[user_frequency]


    def set_nbytes(self, user_nbytes):
        if (user_nbytes >= 16 or user_nbytes < 1): raise "data out of bounds, user_nbytes > 16 or < 1"
        return hex(user_nbytes) # hexes are string objects in python so this function isn't very useful


    def mask_control_reg(self, Reg_ID, mask):
        """
        Applies a given mask to the payload (removes and reapplies the offset before writing)
        Could be written as (TODO: check) 
        payload = rxpayloads[1] | (mask << self.regs_read[Reg_ID].value.Offset)
        """
        rxpayload = self.read_control_reg(Reg_ID)
        print(rxpayload)
        payload = rxpayload[1] >> self.regs_read[Reg_ID].value.Offset
        payload = payload | mask
        payload = payload << self.regs_write[Reg_ID].value.Offset
        print('offset: ', hex(self.regs_write[Reg_ID].value.Offset))
        print('payload: ', hex(payload))
        return sca_chip.write_control_reg(Reg_ID, payload) 


    def enable_channel(self, channel_to_enable):
        enabled_channel = eval(f"Enable_from_Control_Reg.{channel_to_enable}.value")
        print(f"enabling channel {channel_to_enable} through register {enabled_channel.Register}")
        data = 1 << enabled_channel.Bit
        return sca_chip.write_control_reg(self, enabled_channel.Register, data)


    def check_and_convert_user_I2C_channel(self, user_I2C_channel, enabling_channel=False):
        # could extend to have 0-16 and 0-f reading
        assert type(user_I2C_channel) == int, f"channel must be of type int, its type is {type(user_I2C_channel)}"
        assert user_I2C_channel >= 0 and user_I2C_channel < 16, f"channel must be >= 0 and < 16, it is {user_I2C_channel}"
        if enabling_channel == True:
          return f"ENI2C{hex(user_I2C_channel)[-1].upper()}"
        else:
          return channel_id(f"I2C{hex(user_I2C_channel)[-1].upper()}")

    
    def enable_I2C_channel(self, user_I2C_channel):
        print(f"enabling I2C channel {user_I2C_channel}")
        temp = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel, enabling_channel=True)
        return sca_chip.enable_channel(self, I2C_channel)


    def write_I2C_control_reg(self, user_I2C_channel, user_nbytes, user_frequency):
        reg = SCA_Register.I2C_W_CTRL.value
        data_to_write = ((0 | user_nbytes << 2) | sca_chip.set_frequency(self, user_frequency)) << reg.Offset
        print(f"writing to control register of I2C channel {user_I2C_channel}!")
        print(f"data is: {data_to_write} or {bin(data_to_write)} aka {hex(data_to_write)}")
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        return sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, data_to_write, self.sca_addr, 0)


    def read_I2C_control_reg(self, user_I2C_channel):
        print(f"reading control register of I2C channel {user_I2C_channel}!")
        reg = SCA_Register.I2C_R_CTRL.value
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        return sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)


    def read_I2C_status_reg(self, user_I2C_channel):
        print(f"read status of I2C channel {user_I2C_channel}!")
        reg = SCA_Register.I2C_R_STR.value
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        return sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)

   
    def read_I2C_7b(self, user_I2C_channel, address_to_read):
        print(f"start 7 bit read via I2C channel {user_I2C_channel} to device at {address_to_write}")
        reg = SCA_Register.I2C_M_7B_R.value
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        # check that the address is given as hex or int, not as a string
        return sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, address_to_read, self.sca_addr, 0)


    def write_I2C_7b(self, user_I2C_channel, address_to_write):
        print(f"start 7 bit write via I2C channel {user_I2C_channel} to device at {address_to_write}")
        reg = SCA_Register.I2C_M_7B_W.value
        I2C_channel = sca_chip.check_and_convert_user_I2C_channel(self, user_I2C_channel)
        # check that the address is given as hex or int, not as a string
        return sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, address_to_write, self.sca_addr, 0)

######
 
    def read_I2C_data_reg(self, user_I2C_channel, nbytes):
        # untested
        print(f"read data register from channel {user_I2C_channel}")
        for byte in range(nbytes):
            enum_byte = f'BYTE{byte}'
            offset = I2CDataBytesOffset.enum_byte.value
            if 0 <= byte < 4:
                reg = SCA_Register.I2C_R_DATA3.value
            elif 4 <= byte < 8:
                reg = SCA_Register.I2C_R_DATA2.value
            elif 8 <= byte < 12: 
                reg = SCA_Register.I2C_R_DATA1.value
            elif 12 <= byte < 16:
                reg = SCA_Register.I2C_R_DATA0.value
            #reg_data_packet


    def write_I2C_data_reg(self, user_I2C_channel, nbytes, array_data_bytes):
        # untested
        print(f"write to data register of I2C channel {user_I2C_channel}!")
        assert nbytes == len(array_data_bytes), 'nbytes must equal len(array_data_bytes)'
        reg_data_packet = 0
        for byte in range(nbytes):
            enum_byte = f'BYTE{byte}'
            offset = I2CDataBytesOffset.enum_byte.value
            if 0 <= byte < 4:
                reg = SCA_Register.I2C_W_Data0.value 
            elif 4  <= byte < 8:
                reg = SCA_Register.I2C_W_Data1.value
            elif 8  <= byte < 12:
                reg = SCA_Register.I2C_W_Data2.value
            elif 12 <= byte < 16:
                reg = SCA_Register.I2C_W_Data3.value
            reg_data_packet += array_data_bytes[byte] << offset

          # sca_chip.send_command(self, I2C_channel, reg.Length, reg.CMD, reg_data_packet?, self.sca_addr, 0)
          # what do I return? 

    #def check_I2C_data_reg_byte_and_send(self, user_I2C_channel)?
          # if we move to a new register, send the previous data_packet and reset it
          #if byte != 0 and byte % 4 == 0: 
          #    send_command(reg, reg_data_packet)
          #    reg_data_packet = 0
          # if its the final byte and the register has not been sent, send the register
          #elif (byte == nbytes - 1):
          #    send_command(reg, reg_data_packet)
          #    reg_data_packet = 0

    def write_control_reg(self, Reg_ID, data_to_write):
        print(f"write {hex(data_to_write)} to control register {Reg_ID}!")
        reg = eval(f"SCA_Register.CTRL_W_{Reg_ID}.value")
        data_to_write = data_to_write << reg.Offset
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, data_to_write, self.sca_addr, 0)


    def read_control_reg(self, Reg_ID):
        print(f"read control register {Reg_ID}!")
        reg = eval(f"SCA_Register.CTRL_R_{Reg_ID}.value")
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)


    def check_error(self, rxpayload):
        print("checking payload for error flags")
        assert len(rxpayload) == 2, f"rxpayload size must equal 2, it is {len(rxpayload)}"
        # error code is in "first" (leftmost) bit of received header
        header = rxpayload[0]
        error  = (header & (0xff << 24)) >> 24
        if error == 0:
          print(CMDLINECOLOR.PASS + "No errors!" + CMDLINECOLOR.RESET)
          return 0
        print(f"error code is : {hex(error)} also known as {bin(error)}")
        error_binary = bin(error)
        trim_error_binary = error_binary[2:]
        length_trim_error_binary = len(trim_error_binary)
        # make list of indices where error bit is on
        index_where_on = []
        index_where_on = [length_trim_error_binary-1-i for i in range(length_trim_error_binary) if trim_error_binary[i] == "1"]
        for index in index_where_on:
          print(CMDLINECOLOR.ERROR + ErrorFlags[index] + CMDLINECOLOR.RESET)


    def send_command_passthrough(self, channel, length, command, data):
        print("sending user command")
        return sca_chip.send_command(self, channel, length, command, data, self.sca_addr, 0)


    def send_connect(self):
        print("send connect!")
        reg  = SCA_Register.CTRL_W_CRD.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 1)


    def enable_ADC(self):
        print("enabling ADC")
        return sca_chip.enable_channel(self, "ENADC")


    def enable_GPIO(self):
        print("enabling GPIO")
        return sca_chip.enable_channel(self, "ENGPIO")


    def read_SEU(self):
        print("read SEU!")
        reg  = SCA_Register.CTRL_R_SEU.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)


    def reset_SEU(self):
        print("reset SEU!")
        reg  = SCA_Register.CTRL_C_SEU.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)


    def write_GPIO(self, value):
        sca_chip.enable_GPIO(self)
        print(f"write {value} to GPIO!")
        reg  = SCA_Register.GPIO_W_DATAOUT.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, value, self.sca_addr, 0)

       
    def read_GPIO(self):
        print("read GPIO!")
        reg  = SCA_Register.GPIO_R_DATAOUT.value
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)


    def read_ID(self):
        print("read ID!")
        reg = SCA_Register.CTRL_R_ID.value        
        # works with zero or one in data field, but manual specifies data should be one
        print(reg.CMD, type(reg.CMD))
        return sca_chip.send_command(self, reg.Channel, reg.Length, reg.CMD, reg.Data, self.sca_addr, 0)





