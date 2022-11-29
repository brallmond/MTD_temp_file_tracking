import emp
import time 
import uhal 
import logging
import argparse
from lpgbt_controller_dev import *

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
              "fe12_sipm_temp1": {"adc_port": 0, "cur_mask": 1, "gain": 0 , "neg_ref":15},
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

   adc_calib_mapping = {
      "L1": {"slope": 1, "offset": 0, "cur_DAC": 100},
      "L0": {"slope": 1, "offset": 0, "cur_DAC": 100},
   }

   pt1000_resistance_array = [
      602.56, 606.61, 610.66, 614.71, 618.76, 622.80, 626.84, 630.88, 634.92, 638.96,
      643.00, 647.03, 651.06, 655.09, 659.12, 663.15, 667.17, 671.20, 675.22, 679.24,
      683.25, 687.27, 691.29, 695.30, 699.31, 703.32, 707.33, 711.34, 715.34, 719.34,
      723.35, 727.35, 731.34, 735.34, 739.34, 743.33, 747.32, 751.32, 755.30, 759.29,
      763.28, 767.26, 771.25, 775.23, 779.21, 783.19, 787.17, 791.14, 795.12, 799.09,
      803.06, 807.03, 811.00, 814.97, 818.94, 822.90, 826.87, 830.83, 834.79, 838.75,
      842.71, 846.66,850.62, 854.57, 858.53, 862.48, 866.43, 870.38, 874.33, 878.27,
      882.22, 886.16,    890.10,    894.04,    897.99,    901.92,    905.86,    909.80,    913.73,    917.67,
      921.60, 925.53,    929.46,    933.39,    937.32,    941.24,    945.17,    949.09,    953.02,    956.94,
      960.86, 964.78,    968.70,    972.61,    976.53,    980.44,    984.36,    988.27,    992.18,    996.09,
      1000.00, 1003.91, 1007.81, 1011.72, 1015.62, 1019.53, 1023.43, 1027.33,    1031.23, 1035.13,
      1039.03, 1042.92, 1046.82, 1050.71, 1054.60, 1058.49, 1062.38, 1066.27,    1070.16, 1074.05,
      1077.94, 1081.82, 1085.70, 1089.59, 1093.47, 1097.35, 1101.23, 1105.10,    1108.98, 1112.86,
      1116.73, 1120.60, 1124.47, 1128.35, 1132.21, 1136.08, 1139.95, 1143.82,    1147.68, 1151.55,
      1155.41, 1159.27, 1163.13, 1166.99, 1170.85, 1174.70, 1178.56, 1182.41,    1186.27, 1190.12,
      1193.97, 1197.82, 1201.67, 1205.52, 1209.36, 1213.21, 1217.05, 1220.90,    1224.74, 1228.58,
      1232.42, 1236.26, 1240.09, 1243.93, 1247.77, 1251.60, 1255.43, 1259.26,    1263.09, 1266.92,
      1270.75, 1274.58, 1278.40, 1282.23, 1286.05, 1289.87, 1293.70, 1297.52,    1301.33, 1305.15,
      1308.97, 1312.78, 1316.60, 1320.41, 1324.22, 1328.03, 1331.84, 1335.65,    1339.46, 1343.26,
      1347.07, 1350.87, 1354.68, 1358.48, 1362.28, 1366.08, 1369.87, 1373.67,    1377.47, 1381.26,
      1385.05, 1388.85, 1392.64, 1396.43,    1400.22, 1404.00, 1407.79, 1411.58,    1415.36, 1419.14,
      1422.93, 1426.71, 1430.49, 1434.26,    1438.04, 1441.82, 1445.59, 1449.37,    1453.14, 1456.91,
      1460.68, 1464.45, 1468.22, 1471.98,    1475.75, 1479.51, 1483.28, 1487.04,    1490.80, 1494.56,
      1498.32, 1502.08, 1505.83, 1509.59,    1513.34, 1517.10, 1520.85, 1524.60,    1528.35, 1532.10,
      1535.84, 1539.59, 1543.33, 1547.08,    1550.82, 1554.56, 1558.30, 1562.04,    1565.78, 1569.52,
      1573.25, 1576.99, 1580.72, 1584.45,    1588.18, 1591.91, 1595.64, 1599.37,    1603.09, 1606.82,
      1610.54, 1614.27, 1617.99, 1621.71,    1625.43, 1629.15, 1632.86, 1636.58,    1640.30, 1644.01,
      1647.72, 1651.43, 1655.14, 1658.85,    1662.56, 1666.27, 1669.97, 1673.68,    1677.38, 1681.08,
      1684.78, 1688.48, 1692.18, 1695.88,    1699.58, 1703.27, 1706.96, 1710.66,    1714.35, 1718.04,
      1721.73, 1725.42, 1729.10, 1732.79,    1736.48, 1740.16, 1743.84, 1747.52,    1751.20, 1754.88,
      1758.56, 1762.24, 1765.91, 1769.59,    1773.26, 1776.93, 1780.60, 1784.27,    1787.94, 1791.61,
      1795.28, 1798.94, 1802.60, 1806.27,    1809.93, 1813.59, 1817.25, 1820.91,    1824.56, 1828.22,
      1831.88, 1835.53, 1839.18, 1842.83,    1846.48, 1850.13, 1853.78, 1857.43,    1861.07, 1864.72,
      1868.36, 1872.00, 1875.64, 1879.28,    1882.92, 1886.56, 1890.19, 1893.83,    1897.46, 1901.10,
      1904.73, 1908.36, 1911.99, 1915.62,    1919.24, 1922.87, 1926.49, 1930.12,    1933.74, 1937.36,
      1940.98, 1944.60, 1948.22, 1951.83,    1955.45, 1959.06, 1962.68, 1966.29,    1969.90, 1973.51,
      1977.12, 1980.73, 1984.33, 1987.94,    1991.54, 1995.14, 1998.75, 2002.35,    2005.95, 2009.54,
      2013.14, 2016.74, 2020.33, 2023.93,    2027.52, 2031.11, 2034.70, 2038.29,    2041.88, 2045.46,
      2049.05, 2052.63, 2056.22, 2059.80,    2063.38, 2066.96, 2070.54, 2074.11,    2077.69, 2081.27,
      2084.84, 2088.41, 2091.98, 2095.55,    2099.12, 2102.69, 2106.26, 2109.82,    2113.39, 2116.95,
      2120.52]



   # CC specific adc mapping and calibration
   lpgbt_L0.adc_mapping = adc_mapping["L0"]
   lpgbt_L1.adc_mapping = adc_mapping["L1"]
   lpgbt_L0.adc_calib_mapping = adc_calib_mapping["L0"]
   lpgbt_L1.adc_calib_mapping = adc_calib_mapping["L1"]
   lpgbt_L0.pt1000_resistance_array = pt1000_resistance_array
   lpgbt_L1.pt1000_resistance_array = pt1000_resistance_array

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

      #initialize lpgbt L0 and L1 ADC ports. Only L0 initialized for now, PLEASE CHANGE THAT LATER.
      self.lpgbt_L0.set_adc()
      #self.lpgbt_L1.set_adc()
   
