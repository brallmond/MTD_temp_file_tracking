import logging
import argparse
from lpgbt_controller import *

parser =  argparse.ArgumentParser(description='lpgbt controller')
parser.add_argument('-l', dest="link", type=int, default=6, help="Link number (default 6)")
parser.add_argument('-f', dest="fpga", type=str, default='x0', help="fpga (default x0")
parser.add_argument('-addr', dest="address", default="0x1d9", help="Register address (default \"0x0036\")")
parser.add_argument('-val', dest="value", default=[0x40], help="array of write register values (default [0x40])")
parser.add_argument('-length', dest="read_length", type=int, default=1, help="length of the read array (default 1)")
parser.add_argument('-c', dest="connection", default='~/serenity_ku15p_so1_v1_lpgbt_runner-slu9p8x4-project-32301-concurrent-0_220328_1500/hls_connections.xml', help="Connections file")
parser.add_argument('-lpgbt_addr', dest="lpgbt_addr", default="0x70", help="lpgbt address (default \"0x70\")")

args = parser.parse_args()

# get a logger for lpGBT library logging                                                                                                                                                      
lpgbt_logger = logging.getLogger("lpgbt")

# instantiate lpGBT class                                                                                                                                                                     
lpgbt = lpgbt_chip(logger=lpgbt_logger)

lpgbt_cont = lpgbt_cont(path=args.connection, fpga=args.fpga, link=args.link, lpgbt=args.lpgbt_addr)

lpgbt.register_comm_intf(
    name="IC",
    write_regs=lpgbt_cont.write_lpgbt_regs_i2c,
    read_regs=lpgbt_cont.read_lpgbt_regs_i2c,
    default=True
)
#set the output polarization for CCv2 (you will have to run the setup few times):                                                                                                             
lpgbt.force_high_speed_io_invert(invert_data_out=True) # the polarization of the VTRx+ transceivers in CCv2 is inverted in the uplink direction 

#first run this line
#lpgbt.init_lpgbt()  # this should return status 0x13                                                                                                                                                                          
#lpgbt.setup_EPRX() #                                                                                                                                                                            
lpgbt.setup_EC()                                                                                                                                                                             
#lpgbt.setup_ECLKS()

#intialization after ROM                                                                                                                                                                      
print(lpgbt.eclk_status(28))


#print GPIO registers                                                                                                                                                                         
print("--> GPIO registers")
time.sleep(0.2)
print(lpgbt.gpio_status())
time.sleep(0.5)


# register communications interface(s)                                                                                                                                                        
lpgbt_cont.read_lpgbt_regs_i2c(int(args.address,0), args.read_length)

#lpgbt.clock_generator_setup()                                                                                                                                                                

print("---> Setting up EPRX")
lpgbt.setup_EPRX()
# register access methods to control pins                                                                                                                                                     
#lpgbt.register_ctrl_pin_access(                                                                                                                                                              
#    write_pin=lpgbt_cont.write_lpgbt_ctrl_pin,                                                                                                                                               
#    read_pin=lpgbt_cont.read_lpgbt_ctrl_pin                                                                                                                                                  
#)                                                                                                                                                                                            

# communicate with your chip                                                                                                                                                                  
#lpgbt.generate_reset_pulse()                                                                                                                                                                 
# etc                                                                                                                                                                                         
"""                                                                                                                                                                                           
# in order to use a different communication interface                                                                                                                                         
lpgbt.adc_convert(..., comm_intf="I2C")                                                                                                                                                       
lpgbt.adc_convert(..., comm_intf="EC")                                                                                                                                                        
lpgbt.adc_convert(..., comm_intf="IC")                                                                                                                                                        
"""




