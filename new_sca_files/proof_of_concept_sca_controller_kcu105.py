import random # For randint
import sys # For sys.argv and sys.exit
import uhal
import time

#class sca_child( sca_cont):

def send_command(temp1, ch, leng, com, data, sca_addr, reset_SCCEC_flag):

    uhal.disableLogging()

    #connectionFilePath = "Real_connections.xml"
    connectionFilePath = "../Real_connections.xml"
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


    TxValue = (int(com) & 0xff) << 24 | (int(leng) & 0xff) << 16 | (int(ch) & 0xff) << 8 | (int(com) & 0xff)
    # write adc current register
#    print(hex(TxValue))
    EC_Tx_SCA_Header.write(int(TxValue)) 
    hw.dispatch()
    TxValue = data  # data field

    EC_Tx_SCA_Data.write(int(TxValue)) 
    hw.dispatch()

    SCA_Start_CMD.write(int(TxValue)) 
    hw.dispatch()
    RxValue = 0
    time.sleep(.1)
    RxValue = EC_Rx_SCA_Header.read()
    hw.dispatch()
    checkValue = (int(leng) & 0xff << 16) | (int(ch) & 0xff << 8) | (int(com) & 0xff)
    while RxValue != (checkValue) and retrycount < 20:    
        # read SCA results from RxRAM
        RxValue = EC_Rx_SCA_Header.read()
        hw.dispatch()
        retrycount += 1
    rxPayload = []
    rxPayload.append(int(RxValue))
    RxValue = EC_Rx_SCA_Data.read()
    hw.dispatch()
    rxPayload.append(int(RxValue))
    return(rxPayload)

din = send_command(0,0x00, 0x04, 0x06, 0x10000000, 0, 1)
for i in din:
    print(hex(i))
