from random import randint
from sca_controller import *

def test_on(sca_chip):
  # tested, works
  sca_chip.send_connect()
  sca_chip.get_ID()
  sca_chip.check_read_write()

def test_get_ID_explicitly(sca_chip):
  # tested, works
  sca_chip.send_connect()
  reg = SCA_Register.CTRL_R_ID.value
  # read ID without enabling ADC (receive error)
  sca_chip.send_command_passthrough(reg.Channel, reg.Length, reg.CMD, reg.Data)
  # enable ADC
  sca_chip.enable_ADC()
  # read ID now with ADC enabled
  sca_chip.send_command_passthrough(reg.Channel, reg.Length, reg.CMD, reg.Data)


def test_read_write_three_registers(sca_chip):
  # tested (once), works
  sca_chip.send_connect()
  sca_chip.write_control_reg("CRB", randint(1,255))
  sca_chip.read_control_reg("CRB")
  sca_chip.write_control_reg("CRC", randint(1,255))
  sca_chip.read_control_reg("CRC")
  sca_chip.write_control_reg("CRD", randint(1,255))
  sca_chip.read_control_reg("CRD")
 

def test_read_and_reset_SEU(sca_chip):
  # tested, works (only ever read zero in the SEU counter)
  sca_chip.send_connect()
  sca_chip.read_SEU() 
  sca_chip.reset_SEU() 


def test_I2C_enable(sca_chip):
  # tested, works
  sca_chip.send_connect()
  for i in range(1, 16):
    sca_chip.enable_I2C_channel(i)


def test_make_errors(sca_chip):
  # tested, works
  sca_chip.send_connect()
  print(Indicators.INFO + 
        "verify the chip throws no errors for a normal operation" + 
        Indicators.RESET)
  test_on(sca_chip)
  print(Indicators.WARNING + 
        "now purposely making errors" + 
        Indicators.RESET)
  sca_chip.make_command_error()
  sca_chip.make_channel_error()


def test_read_errors(sca_chip):
  # tested, works
  sca_chip.send_connect()
  #test_on(sca_chip)
  error = sca_chip.make_channel_error()
  sca_chip.check_error(error)
  error = sca_chip.make_command_error()
  sca_chip.check_error(error)
  no_error = sca_chip.enable_I2C_channel(1)
  sca_chip.check_error(no_error)


def test_GPIO_read_write(sca_chip):
  # tested (once), works
  sca_chip.send_connect()
  sca_chip.write_GPIO(17)
  sca_chip.read_GPIO()

if __name__ == "__main__":

  chippy = sca_chip()
  
  print("Hi, I'm chippy, your SCA chip! I'm gonna run some tests now...")
  #test_on(chippy)
  #test_get_ID_explicitly(chippy)
  #test_read_write_three_registers(chippy)
  #test_read_and_reset_SEU(chippy)
  #test_I2C_enable(chippy)
  #test_make_errors(chippy)
  #test_read_errors(chippy)
  #test_GPIO_read_write(chippy)


