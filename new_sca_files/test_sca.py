from random import randint
from sca_controller import *

def test_read_ID(sca_chip):
  # tested, works
  sca_chip.send_connect()
  sca_chip.enable_ADC()
  return sca_chip.read_ID()

def test_write_read_three_registers(sca_chip):
  # tested, works
  sca_chip.send_connect()
  sca_chip.write_control_reg("CRB", randint(1,255))
  sca_chip.read_control_reg("CRB")
  sca_chip.write_control_reg("CRC", randint(1,255))
  sca_chip.read_control_reg("CRC")
  sca_chip.write_control_reg("CRD", randint(1,255))
  return sca_chip.read_control_reg("CRD")
 

def test_read_and_reset_SEU(sca_chip):
  # tested, works (only ever read zero in the SEU counter)
  # broken!
  sca_chip.send_reset()
  sca_chip.send_connect()
  sca_chip.read_SEU() 
  return sca_chip.reset_SEU() 


def test_I2C_enable(sca_chip):
  # tested, works
  sca_chip.send_connect()
  for i in range(1, 16):
    if i == 15:
      return sca_chip.enable_I2C_channel(i)
    else:
      sca_chip.enable_I2C_channel(i)


def test_make_command_error(sca_chip):
  # tested, works
  print("make error 0x4 = 0b0000 0100!")
  # supply command to read SCA ID for V1 of the chip
  reg = SCA_Register.CTRL_R_ID.value
  return sca_chip.send_command_passthrough(reg.Channel, reg.Length, 0x91, reg.Data)


def test_make_channel_error(sca_chip):
  # tested, works
  print("make error 0x20 = 0b0010 0000!")
  # supply channel to 0x13 to ID CMD instead of 0x14
  reg = SCA_Register.CTRL_R_ID.value
  return sca_chip.send_command_passthrough(0x13, reg.Length, reg.CMD, reg.Data)


def test_make_length_error(sca_chip):
  # unfinished, having trouble making a length error
  print("make error 0x10 = 0b0100 0000!")
  reg = SCA_Register.CTRL_R_ID.value
  return sca_chip.send_command_passthrough(0x13, reg.Length, reg.CMD, reg.Data)


def test_GPIO_write_read(sca_chip):
  # tested (once), works
  sca_chip.send_connect()
  sca_chip.write_GPIO(17)
  return sca_chip.read_GPIO()


def test_I2C_single_enable(sca_chip, user_I2C_channel=0):
  # tested, works
  return sca_chip.enable_I2C_channel(user_I2C_channel)

def test_I2C_write_read_control_register(sca_chip, user_I2C_channel=0):
  # tested, works
  sca_chip.write_I2C_control_reg(user_I2C_channel, user_nbytes=1, user_frequency="400kHz")
  return sca_chip.read_I2C_control_reg(user_I2C_channel)


if __name__ == "__main__":

  chippy = sca_chip()
  
  print("Hi, I'm chippy, your SCA chip! I'm gonna run some tests now...")

  list_of_tests = [ 
    test_read_ID,
    test_write_read_three_registers,
    test_read_and_reset_SEU, #broken!
    test_I2C_enable,
    test_make_command_error,
    test_make_channel_error,
    #test_make_length_error,
    test_GPIO_write_read,
  ]

  error_tests = [
    test_read_ID,
    test_make_command_error,
    test_make_channel_error,
    #test_make_length_error, #unfinished!
  ]

  test_on = [
    test_read_ID,
    test_write_read_three_registers,
  ]

  test_I2C = [
    test_I2C_single_enable,
    test_I2C_write_read_control_register,
  ]


  list_to_test = list_of_tests # "make errors" tests don't work in this list
  list_to_test = test_on
  list_to_test = error_tests
  list_to_test = test_I2C

  for i,test in enumerate(list_to_test):
    print(CMDLINECOLOR.INFO + 
          f"########## TEST {i} ##########" + '\n' +
          f"Name: {test} " + 
          CMDLINECOLOR.RESET)
    rxpayload = test(chippy)
    chippy.check_error(rxpayload)

