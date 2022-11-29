import emp
import time 
import uhal 

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
uhal.setLogLevelTo(uhal.LogLevel.WARNING)

from lpgbt_control_lib import LpgbtV1
from lpgbt_control_lib.lpgbt import lpgbt_accessor
from chip import Chip

class lpgbt_com(Chip):
    addr_w = []
    data_w = []
    command = []
    write_t = False
    execute = 0    
    def ic_opt_write(self,addr, values, lpgbt_addr):
        self.addr_w.append(addr)
        self.data_w.append(values)
        self.write_t = True
        self.command.append(True)

    def ic_write(self, addr, values, lpgbt_addr):
        if(not hasattr(values, "__len__")): 
            values = [values]
        if(not hasattr(addr, "__len__")):
            addr = [addr]
        self.emp_cont.getSCCIC().icBlockWrite(addr, values, lpgbt_addr)
#        self.emp_cont.getSCCIC().icScatteredWrite(addr, values, lpgbt_addr)
        time.sleep(0.5)

    def ic_read(self, addr, nwords, lpgbt_addr):
        if(self.write_t == True):
            self.emp_cont.getSCCIC().icScatteredWrite(self.addr_w, self.data_w, lpgbt_addr)
            self.addr_w = []
            self.data_w = []
            self.write_t = False
        if nwords > 0:
            values = self.emp_cont.getSCCIC().icReadBlock(addr, nwords, lpgbt_addr)
            print("lpGBT addr : 0x{:02x}".format(lpgbt_addr))
            for value in values:
                print(" | addr : 0x{:04x} | value 0x{:02x} | ".format(addr, value))
                addr += 1
                #time.sleep(0.5)
        else:
            print("Invalid number of word : {:d}".format(nwords))
        time.sleep(0.5)
        return values

class lpgbt_cont():
    # low level access to control pins
    # GPIO_MAP = [
    #     LpgbtV1.CTRL_RSTB: 0,
    #     LpgbtV1.CTRL_ADDR: 1,
        # ... add a mapping to your hardware GPIOs for all control pins
    # ]
    
    def __init__(self, path, fpga, link, lpgbt):
        self.lpgbt_com = lpgbt_com()
        self.lpgbt_com.hw_interface(path, fpga, link)
        self.lpgbt_addr = lpgbt
        #    def write_lpgbt_ctrl_pin(self, pin_name, value):
        #gpio_id = GPIO_MAP[pin_name]
        # TODO: write 'value' to your hardware GPIO

        #    def read_lpgbt_ctrl_pin(self, pin_name):
        #       gpio_id = GPIO_MAP[pin_name]
        # gpio_val = # TODO read value of hardware GPIO
        #      return gpio_val

    # low level access to I2C interface
    def write_lpgbt_regs_i2c(self, reg_addr, reg_vals):
        # some_i2c_master.write_regs(
        #     device_addr=0x70
        #     addr_width=2,
        #     reg_addr=reg_addr,
        #     data=reg_vals
        # )
        self.lpgbt_com.ic_write(reg_addr, reg_vals, lpgbt_addr=int(self.lpgbt_addr,0))

    def read_lpgbt_regs_i2c(self, reg_addr, read_len):
        # values = some_i2c_master.read_regs(
        #     device_addr=0x70,
        #     addr_width=2,
        #     reg_addr=reg_addr,
        #     read_len=read_len
        # )
        values = self.lpgbt_com.ic_read(reg_addr, read_len, lpgbt_addr=int(self.lpgbt_addr,0))
        return values

class lpgbt_chip(LpgbtV1):
    def init_lpgbt(self):
        print("initializing lpgbt with the lpgbt_control_lib")


        #self.clock_generator_setup()

        self.line_driver_setup()

        self.equalizer_setup() 

        #self.config_done()

        self.config_done_and_wait_for_ready()

        print("lpgbt is initialized")
    def setup_EC(self):
        self.eprx_general_config()
        self.eptx_ec_setup()
        self.eprx_ec_setup()
        self.eclk_setup(self.indECELINK,freq=self.clk40M) 
    def setup_ECLKS(self):
        for eind in range(self.nELINKS):
            self.eclk_setup(eind,freq=self.clk160M)
    @lpgbt_accessor
    def eprx_channel_config_write(
        self,
        group_id,
        channel_id,
        term=True,
        ac_bias=False,
        invert=False,
        phase=0,
        equalizer=0,
    ):
        """
        
        Optimization of original eprx_channel_config from lpgbt.py 
        which reduced at a minimum the number of reads of lpGBT registers

        Configures an ePortRx channel

        Arguments:
            group_id: ePortRx group to configure
            channel_id: channel in the ePortRx to configure
            term: input termination control
            ac_bias: AC bias generation control
            invert: data inversion control
            phase: static data phase control
            equalizer: input equalizer control
        
        """
        # pylint: disable=too-many-arguments
        assert group_id in range(7), "Invalid ePortRx group"
        assert channel_id in range(4), "Invalid ePortRx channel"
        assert phase in range(16), "Invalid ePortRX phase"
        assert equalizer in range(4), "Invalid ePortRX equalizer configuration"
        
        # To configure channels we have one register for each eLink in each of the 7 eGroups in Rx
        # We have to write them all. Do not read, this will overwrite what's already written there

        reg = self.EPRX00CHNCNTR.address + group_id * 4 + channel_id

        reg_val = phase << self.EPRX00CHNCNTR.EPRX00PHASESELECT.offset

        if invert:
            reg_val |= self.EPRX00CHNCNTR.EPRX00INVERT.bit_mask

        if term:
            reg_val |= self.EPRX00CHNCNTR.EPRX00TERM.bit_mask

        if ac_bias:
            reg_val |= self.EPRX00CHNCNTR.EPRX00ACBIAS.bit_mask

        if equalizer & 0x2:
            reg_val |= self.EPRX00CHNCNTR.EPRX00EQ.bit_mask

        self.write_reg(reg, reg_val)
        
        # There is one register for pairs of groups
        # EPRXEQ10CONTROL EPRXEQ32CONTROL EPRXEQ54CONTROL EPRXEQ76CONTROL

        req_eq = self.EPRXEQ10CONTROL.address + int(group_id / 2)
        reg_val = 0

        chan_mask = 1 << (group_id * 4 + channel_id) % 8
        reg_val &= chan_mask
        if equalizer & 0x1:
            reg_val |= chan_mask
        self.write_reg(req_eq, reg_val)
    
    @lpgbt_accessor
    def eptx_all_group_setup(
        self,
        data_rate=0,
        chn0_enable=True,
        chn1_enable=True,
        chn2_enable=True,
        chn3_enable=True,
        mirror_enable=False,
    ):
        """
           This function configures all ePortTx groups channel 0-3 for all 
           eGroups. Does not read any register and just writes them (one register, one write)
 
           Arguments:
            
            data_rate: data rate that will be associated to all groups (EPORTTX_X2, EPORTTX_X4, ...)
            chn0_enable: state of channel 0
            chn1_enable: state of channel 1
            chn2_enable: state of channel 2
            chn3_enable: state of channel 3
            mirror_enable: mirror function control eGroup
        """

        if isinstance(data_rate, int): assert data_rate in range(4), "Invalid ePortTx data rate"
        elif isinstance(data_rate, list): assert all(i in range(4) for i in data_rate) and len(data_rate) == 4, "List ePortTx data rate should have 4 entries with values between 0-3"
        else: raise TypeError("data_rate argument should be an integer (to set rate for all eGroups) or list of 4 entries, one data_rate for each eGroup") 
        
        if isinstance(mirror_enable, list): assert all(isinstance(i, bool) for i in mirror_enable) and len(mirror_enable) == 4, "mirror_enable list argument should contain 4 type bool"

        # Data rate control for ePortTx (EPTXDATARATE) is a 8 bit register
        # 2 bits associated to each of the 4 eGroups. Values of the 2 bits range from 
        # 0 to 3 respectively for 0, 80, 160, 320 Mbps
        
        # Initialize to 0 as we are setting it for alll registers. Do not 
        # need to read the register, will be overwrited anyway
        data_rate_reg_val = 0
        
        # If integer data_rate as argument, set this value for all channels
        # otherwise it should be a list then each entry associated 
        # to the group by index in the list
        if isinstance(data_rate, int): data_rate = [data_rate]*4
         
        for group_id, d_rate in enumerate(data_rate):
           data_rate_reg_val |= data_rate[group_id] << (group_id * 2)
         
        self.write_reg(self.EPTXDATARATE, data_rate_reg_val)
        
        # Reading the channel enable register. There are two of them 
        # one for groups 0-1 and one for group 2-3 (EPTX10Enable, EPTX32Enable)
        
        enable_reg_10, enable_reg_32 = self.EPTX10ENABLE.address, self.EPTX32ENABLE.address
        
        #for idx, register_address in [enable_reg_10, enable_reg_32]:
        
        # disabling / enabling the registers. First 4 bits are for groups 0-2, last 4 for groups 1-3
        enable_reg_val = 0
         
        # These if-else build an 8 bit, channels are equally enabled for all groups
        if chn0_enable:
            enable_reg_val |= self.EPTX10ENABLE.EPTX00ENABLE.bit_mask | self.EPTX10ENABLE.EPTX10ENABLE.bit_mask
        if chn1_enable:
            enable_reg_val |= self.EPTX10ENABLE.EPTX01ENABLE.bit_mask | self.EPTX10ENABLE.EPTX11ENABLE.bit_mask
        if chn2_enable:
            enable_reg_val |= self.EPTX10ENABLE.EPTX02ENABLE.bit_mask | self.EPTX10ENABLE.EPTX12ENABLE.bit_mask
        if chn3_enable:
            enable_reg_val |= self.EPTX10ENABLE.EPTX03ENABLE.bit_mask | self.EPTX10ENABLE.EPTX13ENABLE.bit_mask

        self.write_reg(enable_reg_10, enable_reg_val)
        self.write_reg(enable_reg_32, enable_reg_val)
        
        # EPTXCONTROL is a 4 bit register for mirror of EportTx

        # Initialize it to zero, we will set it for all eGroups so it is 
        # useless to read current value in lpGBT, will be overwritten
        mirror_reg_val = 0
        
        # if mirror_enable argument is a bool then we convert it into list of equal values
        # otherwise it should be a lis of four entries one per eGroup
        if isinstance(mirror_enable, bool): mirror_enable = [mirror_enable]*4

        for group_id, mirror in enumerate(mirror_enable):
            if mirror:
                mirror_reg_val |= 1 << group_id
        
        self.write_reg(self.EPTXCONTROL, mirror_reg_val)

    def eptx_group_output_driver_config(
        self,
        group_id,
        pre_emphasis_width=0,
        invert=False
    ):

        """
           This is the second part of tthe original eptx_channel_config.
           We split this because if the whole group eLinks share the same configuration
           Then we can minimise the number of write calls by writing a full register 
           (instead 4 out of 8 bits)

           eLinks output driver strengths setting registers come in pairs (e.g. channel 0 and 1 in group 0)
           EPTX01_00CHNCNTR -> 01_00 -> 01: group 0 channel 1, 00: group 0 channel 0
           EPTX03_02ChnCntr -> 03_02 -> 03: group 0 channel 3, 02: group 0 channel 2
           Each register is 8 bits.
           bit [0:3] for lower channel index width of pre-emphasis
           bit [3] for lower channel index data inverter 
           bit [4:6] for higher index width of pre-emphasis
           bit [7] for higher index data inverter
        """

        assert pre_emphasis_width in range(8), "Invalid preemphasis width"
        
        #eLinks output driver strengths setting registers come in pairs (e.g. channel 0 and 1 in group 0)
        #EPTX01_00CHNCNTR -> 01_00 -> 01: group 0 channel 1, 00: group 0 channel 0
        #EPTX03_02ChnCntr -> 03_02 -> 03: group 0 channel 3, 02: group 0 channel 2
        #Each register is 8 bits.
        #bit [0:3] for lower channel index width of pre-emphasis
        #bit [3] for lower channel index data inverter 
        #bit [4:6] for higher index width of pre-emphasis
        #bit [7] for higher index data inverter
        
        # so given that 0-1 channels and 2-3 channels share registers we 
        # can set it for one channel (all customization equal for the other one)
        
        for channel_id in [0,2]:
           # The address retrieved is the same for channel 0-1 and 2-3.
           secondary_reg_adr = (
               self.EPTX01_00CHNCNTR.address + group_id * 2 + int(channel_id / 2)
           )
          
           # we do not need to read the register as we set the 
           # configuration for both cannel. Initialize to 0
           secondary_reg_val = 0
           #secondary_reg_val &= ~(0xF << 4 * (channel_id % 2))
           secondary_msk = pre_emphasis_width
           if invert:
               # pre_emphasis_width is at most 7 = 0b111 and EPTX00INVERT.bit_mask is 8 = 0b1000 so it will 
               # turn on or off the last bit
               secondary_msk |= self.EPTX01_00CHNCNTR.EPTX00INVERT.bit_mask 
           for id_ in [0,1]:
              # if channel_id is 0 we make the or witch channel_id = 0 and channel_id + 1 = 1
              # same for channel_id =2 and channel_id + 1 = 3
              secondary_reg_val |= secondary_msk << 4 * ((channel_id+id_) % 2)

           self.write_reg(secondary_reg_adr, secondary_reg_val)

    def eptx_channel_config_write(
        self,
        group_id,
        channel_id,
        drive_strength=4,
        pre_emphasis_mode=2,
        pre_emphasis_strength=0,
        #pre_emphasis_width=0,
        #invert=False,
    ):
        """
        Optimization of original eptx_channel_config from lpgbt.py 
        which reduces at a minimum the number of reads of lpGBT registers

        Configures an ePortTx channel

        Arguments:
            group_id: ePortTx group
            channel_id: ePortTx group channel
            drive_strength: output driver strength
            pre_emphasis_mode: output driver pre-emphasis mode
            pre_emphasis_strength: output driver pre-emphasis strength
            pre_emphasis_width: output driver pre-emphasis width
            invert: output data inversion control
        """
        # pylint: disable=too-many-arguments
        assert group_id in range(4), "Invalid ePortTx group"
        assert channel_id in range(4), "Invalid ePortTx channel"
        assert drive_strength in range(8), "Invalid drive strength configuration"
        assert pre_emphasis_strength in range(8), "Invalid preemphasis strength"
        assert pre_emphasis_mode in range(4), "Invalid preemphasis mode"
        assert pre_emphasis_width in range(8), "Invalid preemphasis width"
        
        # First address for channel 0 group 0 then increments as a function of the group and the channel id
        primary_reg_adr = self.EPTX00CHNCNTR.address + group_id * 4 + channel_id

        # EPTXMN0CHNCNTR Control register for output driver of channel N in group M
        # 8 bits: 
        # bit [0:2] dedicated to DriveStrength
        # bit [3:4] dedicated to pre-emphasis mode
        # bit [5:7] dedicated to pre-emphasis strength
        
        # the offset for driverStrength is 0
        # the offset for pre-emphasis mode is 3
        # the offset for pre-emphasis strength is 5 

        # primary_reg_val is now a 3 bit binary  
        primary_reg_val = (
            drive_strength << self.EPTX00CHNCNTR.EPTX00DRIVESTRENGTH.offset
        )
        # as pre_emphasis_mode has offset 3, the first 3 bits are not touched. pre_emphasis_mode is a 2 bit number
        primary_reg_val |= (
            pre_emphasis_mode << self.EPTX00CHNCNTR.EPTX00PREEMPHASISMODE.offset
        )
        # as pre_emphasis_strength has offset 5, the first 5 bits are not touched. pre_emphasis_strength is a 3 bit number
        primary_reg_val |= (
            pre_emphasis_strength << self.EPTX00CHNCNTR.EPTX00PREEMPHASISSTRENGTH.offset
        )
    
        # write to register
        self.write_reg(primary_reg_adr, primary_reg_val)


    def setup_EPTX(
       self, 
       data_rate=3,
       drive_strength=3,
       pre_emphasis_mode=2,
       pre_emphasis_strength=0,
       pre_emphasis_width=0,
       mirror_enable=False
       ):

       """
          data_rate = 0 -> ePortTx disabled
          data_rate = 1 -> ePortTx 80 Mbps
          data_rate = 2 -> ePortTx 160 Mbps
          data_rate = 3 -> ePortTx 320 Mbps
       """ 

       # configure ePortTx channels.
       for group_idx in range(self.nTxEGROUPS):

          # For now group 3 channel 0 is connected to GBT-SCA. Leave it untouched because we do not know the 
          # data rate. This will need to be fixed
          if group_idx == self.indECEGROUP: continue

          # configure ePortTx groups with input data Rate and all channels enabled.
          self.eptx_all_group_setup(data_rate=data_rate, mirror_enable=mirror_enable)
          time.sleep(0.5)
          # configure the output driver, samee for all channels and all groups
          self.eptx_group_output_driver_config(group_idx, pre_emphasis_width=0, invert=False)
          time.sleep(0.5)
          for channel_idx in range(self.nELINKSxEGROUP):
             self.eptx_channel_config_write(group_ixd, 
                channel_idx, 
                drive_strength=drive_strength, 
                pre_emphasis_mode=pre_emphasis_mode, 
                pre_emphasis_strength=pre_emphasis_strength
             )
             time.sleep(0.5)

    def setup_EPRX(self):

        #sets up dll config 
        print("--> Setting epr general config ")
        self.eprx_general_config(dll_current=3,
           dll_confirm_count=3,
           coarse_lock_detection=False,
           data_gating_enable=False,
           fsm_clk_always_on=False,
           reinit_enable=True
        )
        print("--> Finished")
        time.sleep(1.5)
 
        # configure ePortRx groups with disabled data rate, fixed phase and all the channels enabled.
        for group_idx in range(self.nRxEGROUPS):

           # For now group 3 channel 0 is connected to GBT-SCA. Leave it untouched because we do not know the 
           # data rate. This will need to be fixed
           if group_idx == self.indECEGROUP: continue
           print("Setting group setup for group {}".format(group_idx))
           # Official function from lpgbt.py because it does not perform reads
           self.eprx_group_setup(group_idx, 
              data_rate=1, 
              track_mode=2, 
              chn0_enable=True, 
              chn1_enable=True, 
              chn2_enable=True, 
              chn3_enable=True
           )
           time.sleep(1.5)

           # configure ePortRx channels with enabled 100 Ohm termination, common mode generation and disabled 
           # invertion, zero phase, ad zero equalization control.
           for channel_idx in range(self.nELINKSxEGROUP):
              print("--> Setting channel config for group {} channel {}".format(group_idx, channel_idx))
              self.eprx_channel_config_write(group_idx, channel_idx, term=True, ac_bias=True, invert=False, phase=0, equalizer=0)
              time.sleep(1.5)

           
    nELINKS = 28
    indECELINK = 28
    indECEGROUP = 3
    clk320M = 4
    clk160M = 3
    clk40M = 1
    nELINKSxEGROUP = 4
    nTxEGROUPS = 4
    nRxEGROUPS = 7
