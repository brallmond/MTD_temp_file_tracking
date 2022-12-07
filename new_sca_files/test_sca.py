from dev_sca_controller import *

foo = sca_chip()

# main
#foo.send_connect()
#foo.enable_ADC()

# test I2C enable
#for i in range(1,16):
#  print(i)
#  foo.enable_I2C_channel(i)

# test ON
foo.send_connect()
foo.get_ID()
foo.check_read_write()

# test get_ID explicitly
#foo.send_connect()
#reg = SCA_Register.CTRL_R_ID.value
# read ID without enabling ADC
#foo.send_command_passthrough(reg.Channel, reg.Length, reg.CMD, reg.Data)
# enable ADC
#foo.enable_ADC()
# read ID now with ADC enabled
#foo.send_command_passthrough(reg.Channel, reg.Length, reg.CMD, reg.Data)

# display errors
#foo.make_command_error()
#foo.make_channel_error()

# test read-write three registers
#foo.write_control_reg("CRB", 1)
#foo.read_control_reg("CRB")
#foo.write_control_reg("CRC", 2)
#foo.read_control_reg("CRC")
#foo.write_control_reg("CRD", 3)
#foo.read_control_reg("CRD")

# test read and reset SEU
#foo.read_SEU()
#foo.reset_SEU()


