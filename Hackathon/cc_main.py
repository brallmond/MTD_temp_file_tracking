import logging
import argparse
from lpgbt_controller_dev import *
from cc_controller import *

parser =  argparse.ArgumentParser(description='lpgbt controller')
parser.add_argument('-l', dest="link", type=int, default=6, help="Link number (default 6)")
parser.add_argument('-f', dest="fpga", type=str, default='x0', help="fpga (default x0")
parser.add_argument('-addr', dest="address", default="0x1d9", help="Register address (default \"0x0036\")")
parser.add_argument('-val', dest="value", default=[0x40], help="array of write register values (default [0x40])")
parser.add_argument('-length', dest="read_length", type=int, default=1, help="length of the read array (default 1)")
parser.add_argument('-c', dest="connection", default='~/serenity_ku15p_so1_v1_lpgbt_runner-slu9p8x4-project-32301-concurrent-0_220328_1500/hls_connections.xml', help="Connections file")
parser.add_argument('-lpgbt_addr', dest="lpgbt_addr", default="0x70", help="lpgbt address (default \"0x70\")")

args = parser.parse_args()


cc = cc_cont()

cc.setup_L0(args.connection, args.fpga, args.link, args.lpgbt_addr) 

cc.useL0()

print("---> vddaa_power input: ", cc.lpgbt_L0.read_gpio_input("vddaa_raf_power"))

cc.lpgbt_L0.write_gpio_output("calib_raf_preemp_dur", 0)
print("---> read calib_preemp_dur register: ", cc.lpgbt_L0.read_gpio_output("calib_raf_preemp_dur"))
cc.lpgbt_L0.write_gpio_output("calib_raf_preemp_dur", 1)
print("---> read calib_preemp_dur register: ", cc.lpgbt_L0.read_gpio_output("calib_raf_preemp_dur"))


for key in cc.lpgbt_L0.adc_mapping.keys():
    print("----->")
    print(key, hex(cc.lpgbt_L0.read_adc(key)))
    print("----->")

# cc.setup_SCA(args.connection, args.fpga, args.link) #is sca addr unique and always the same?
# cc.setup_SCA_I2C()
