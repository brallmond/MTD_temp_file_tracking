import emp
import time 
import uhal 
import logging
import argparse
from lpgbt_controller_dev import *
from sca_controller import *

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
uhal.setLogLevelTo(uhal.LogLevel.WARNING)

class cc_cont():

   lpgbt_logger = logging.getLogger("lpgbt")
   
   # instantiate lpGBT class                                                                                                                                                                     
   lpgbt_L0 = lpgbt_chip(logger=lpgbt_logger) 
   lpgbt_L1 = lpgbt_chip(logger=lpgbt_logger)
   
   gpio_mapping = {

       "L1": {
          "clk_raf_preemp_conf": {"gpio_port": 0, "dir": 1, "current_dir": 0},
          "elink_raf_preemp_dur": {"gpio_port": 1, "dir": 1, "current_dir": 0},
          "not_connected_1": {"gpio_port": 2, "dir": 0, "current_dir": 0},
          "calib_raf_preemp_dur": {"gpio_port": 3, "dir": 1, "current_dir": 0},
          "not_connected_2": {"gpio_port": 4, "dir": 0, "current_dir": 0},
          "clk_raf_preemp_dur": {"gpio_port": 5, "dir": 1, "current_dir": 0},
          "vddac_power": {"gpio_port": 6, "dir": 0, "current_dir": 0},
          "not_connected_3": {"gpio_port": 7, "dir": 0, "current_dir": 0},
          "elink_raf_preemp_conf": {"gpio_port": 8, "dir": 1, "current_dir": 0},
          "not_connected_4": {"gpio_port": 9, "dir": 0, "current_dir": 0},
          "not_connected_5": {"gpio_port": 10, "dir": 0, "current_dir": 0},
          "calib_raf_preemp_conf": {"gpio_port": 11, "dir": 1, "current_dir": 0},
          "vddad_power": {"gpio_port": 12, "dir": 0, "current_dir": 0}, 
          "not_connected_6": {"gpio_port": 13, "dir": 0, "current_dir": 0},
          "2p5v_power": {"gpio_port": 14, "dir": 0, "current_dir": 0},
          "not_connected_7": {"gpio_port": 15, "dir": 0, "current_dir": 0},
       },

       "L0": {
          "not_connected_1": {"gpio_port": 0, "dir": 0, "current_dir": 0},
          "not_connected_2": {"gpio_port": 1, "dir": 0, "current_dir": 0},
          "clk_raf_preemp_conf": {"gpio_port": 2, "dir": 1, "current_dir": 0},
          "elink_raf_preemp_dur": {"gpio_port": 9, "dir": 1, "current_dir": 0},
          "calib_raf_preemp_dur": {"gpio_port": 7, "dir": 1, "current_dir": 0},
          "clk_raf_preemp_dur": {"gpio_port": 10, "dir": 1, "current_dir": 0},
          "vddaa_power": {"gpio_port": 3, "dir": 0, "current_dir": 0},
          "elink_raf_preemp_conf": {"gpio_port": 8, "dir": 1, "current_dir": 0},
          "calib_raf_preemp_conf": {"gpio_port": 6, "dir": 1, "current_dir": 0},
          "vddab_power": {"gpio_port": 5, "dir": 0, "current_dir": 0},
          "1p2v_power": {"gpio_port": 4, "dir": 0, "current_dir": 0},
          "not_connected_3": {"gpio_port": 11, "dir": 0, "current_dir": 0},
          "not_connected_4": {"gpio_port": 12, "dir": 0, "current_dir": 0},
          "not_connected_5": {"gpio_port": 13, "dir": 0, "current_dir": 0},
          "not_connected_6": {"gpio_port": 14, "dir": 0, "current_dir": 0},
          "not_connected_7": {"gpio_port": 15, "dir": 0, "current_dir": 0},
      },
    }
   


   adc_mapping = {

           "L1": {
              "fe12_sipm_temp1": {"adc_port": 0, "cur_mask": 1, "gain": 0 , "neg_ref":15 },
              "fe12_sipm_temp2": {"adc_port": 1, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "pccB_temp1": {"adc_port": 2, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "pccB_temp2": {"adc_port": 3, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "vddac_voltage": {"adc_port": 4, "cur_mask": 0, "gain": 0 , "neg_ref":15},
              "vddad_voltage": {"adc_port": 5, "cur_mask": 0, "gain": 0 , "neg_ref":15},
              "ccboard_temp2": {"adc_port": 6, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "ccboard_temp3": {"adc_port": 7, "cur_mask": 1, "gain": 0 , "neg_ref":15},
           },

           "L0": {
              "fe6_sipm_temp1": {"adc_port": 0, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "fe6_sipm_temp2": {"adc_port": 1, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "pccA_temp1": {"adc_port": 2, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "pccA_temp2": {"adc_port": 3, "cur_mask": 1, "gain": 0 , "neg_ref":15},
              "vddaa_voltage": {"adc_port": 4, "cur_mask": 0, "gain": 0 , "neg_ref":15},
              "vddab_voltage": {"adc_port": 5, "cur_mask": 0, "gain": 0 , "neg_ref":15},
              "vin_voltage": {"adc_port": 6, "cur_mask": 0, "gain": 0 , "neg_ref":15},
              "ccboard_temp1": {"adc_port": 7, "cur_mask": 1, "gain": 0 , "neg_ref":15},
           },

       }


   # initializing the ADC
   lpgbt_L0.adc_mapping = adc_mapping["L0"]
   lpgbt_L1.adc_mapping = adc_mapping["L1"]

   def useL1(self):
      
      map_l1 = self.gpio_mapping["L1"]
      map_l0 = self.gpio_mapping["L0"]
 
      
      for key in map_l1.keys():
         map_l1[key]["current_dir"] = map_l1[key]["dir"]

      for key in map_l0.keys():
         map_l0[key]["current_dir"] = 0

      self.lpgbt_L0.gpio_mapping = map_l0
      self.lpgbt_L1.gpio_mapping = map_l1
      
      self.lpgbt_L0.set_gpio_direction()
      #self.lpgbt_L1.set_gpio_direction()
 
      print("---> Done")
      
   def useL0(self): 

      map_l1 = self.gpio_mapping["L1"]
      map_l0 = self.gpio_mapping["L0"]

      for key in map_l0.keys():
         map_l0[key]["current_dir"] = map_l0[key]["dir"]

      for key in map_l1.keys():
         map_l1[key]["current_dir"] = 0

      self.lpgbt_L0.gpio_mapping = map_l0
      self.lpgbt_L1.gpio_mapping = map_l1
      
      self.lpgbt_L0.set_gpio_direction()
      #self.lpgbt_L1.set_gpio_direction()

      print("---> Done")


   def setup_L0(self, connection, fpga, link, lpgbt_addr):
     
      lpgbt_cont_ = lpgbt_cont(path=connection, fpga=fpga, link=link, lpgbt=lpgbt_addr)
    
      self.lpgbt_L0.register_comm_intf(
       name="IC",
       write_regs=lpgbt_cont_.write_lpgbt_regs_i2c,
       read_regs=lpgbt_cont_.read_lpgbt_regs_i2c,
       default=True
      )
      
      self.lpgbt_L0.force_high_speed_io_invert(invert_data_out=True) # the polarization of the VTRx+ transceivers in CCv2 is inverted in the uplink direction 

      #first run this line
      # lpgbt.init_lpgbt()  # this should return status 0x13 
      #lpgbt.setup_EPRX() #                                                                                                                                                                            
      self.lpgbt_L0.setup_EC()
      #lpgbt.setup_ECLKS()

      #intialization after ROM                                                                                                                                                                      
      print(self.lpgbt_L0.eclk_status(28))

# sca
    def setup_SCA(self, connection, fpga, link, sca_addr):

        sca_chip = sca_chip(path=connection, fpga=fpga, link=link)
   
    def enable_SCA_I2C(self):

       sca_chip.init_i2c(0) # values from 0 to 15 are valid, but we only use 0 and 1
       sca_chip.init_i2c(1) 
