import logging
import argparse
import emp
import time
import uhal

from sca_controller import sca_com, sca_cont

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
uhal.setLogLevelTo(uhal.LogLevel.WARNING)

parser =  argparse.ArgumentParser(description='sca controller')
parser.add_argument('-l', dest="link", type=int, default=6, help="Link number (default 6)")
parser.add_argument('-f', dest="fpga", type=str, default='x0', help="fpga (default x0")
parser.add_argument('-addr', dest="address", default="0x1d9", help="Register address (default \"0x0036\")")
parser.add_argument('-c', dest="connection", default='~/serenity_ku15p_so1_v1_lpgbt_runner-slu9p8x4-project-32301-concurrent-0_220328_1500/hls_connections.xm\
l', help="Connections file")
parser.add_argument('-sca_addr', dest="sca_addr", default="0x0000", help="sca address (default \"0x0000\")")
parser.add_argument('-d', dest="data", type=str, help="data   (32bits) : D[31:0] in the each command table at GBT-SCA.")
parser.add_argument('-r', dest="reset", type=int, help="reset SCCEC (0=No, 1=Yes)", default=0)

args = parser.parse_args()
ch, leng, com, data = args.data.split(':')

sca_cont = sca_cont(path=args.connection, fpga=args.fpga, link=args.link)
#sca_cont.send_command(ch, leng, com, data, args.sca_addr, args.reset)  

print('1st command: ')

ic_ch = '0x0'
ic_leng = '4' 
ic_data = '0x0'
ic_com = '0x3'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1] | 0x10000000
print('new value: ', hex(new_value))


print(' ')
print('2nd command')
ic_ch = '0x0'
ic_leng = '4'
ic_data = hex(new_value)
ic_com = '0x2'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))

print(' ')
print('3rd command')

ic_ch = '0x0'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x3'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1] 
print('new value: ', hex(new_value))

print(' ')
print('4th command')
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x12000000'
ic_com = '0x30'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1] 
print('new value: ', hex(new_value))

print(' ')
print('5th command')
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x31'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))


print(' ')
print('6th command')
import time
time.sleep(5)

ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x50'
ic_com = '0xde'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1] 
print('new value: ', hex(new_value))

print(' ')
print('6.1th command')
time.sleep(5)
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x11'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))


print(' ')
print('7th command')
time.sleep(5)
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x41'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))

print(' ')
print('8th command')
time.sleep(5)
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x51'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))

print(' ')
print('9th command')
time.sleep(5)
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x61'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))

print(' ')
print('10th command')
time.sleep(5)
ic_ch = '0x4'
ic_leng = '4'
ic_data = '0x0'
ic_com = '0x71'

reg_addr = '0x12'
sca_addr = args.sca_addr

rxpayloads = sca_cont.send_command(ic_ch, ic_leng, ic_com, ic_data, args.sca_addr, 0)
new_value = rxpayloads[1]
print('new value: ', hex(new_value))

#sca_cont.send_command(ch, leng, com, data, args.sca_addr, args.reset)
#I2C_ADDR = int('0x41040404', 16)
#I2C_ADDR = int('0x30040301', 16)
#I2C_ADDR = int('0xde040403', 16)
#print(I2C_ADDR)
#sca_cont.read_sca_regs_i2c(int('0x50', 16), 1)                                                                                                               
#sca_cont.write_sca_regs_i2c(int('0x50', 16), 1)
