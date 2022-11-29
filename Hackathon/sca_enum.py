from enum import Enum, IntEnum, unique
from collections import namedtuple

Command_properties_type = namedtuple('Command_properties_type',
                                     'Channel CMD Length, Operation Offset Data Function_Description')
I2C_configuration_registers_properties_type = namedtuple('I2C_configuration_registers_properties_type',
                                                         'Mode Function')

WORD_LENGTH = 4


class Operation(IntEnum):
    Read = 0
    Write = 1
    ReadWrite = 2


class Flag(IntEnum):
    """
    Calls Return
    """
    Generic_error_flag = 0
    Invalid_channel_request = 1
    Invalid_command_request = 2
    Invalid_transaction_number_request = 3
    Invalid_length = 4
    Channel_not_enabled = 5
    Channel_currently_busy = 6
    Command_in_treatment = 7


# Not unique Enum
class Channel(Enum):
    """

    """
    CTRL = 0x00  # SCA configuration registers
    SPI = 0x01  # SPI
    GPIO = 0x02  # Parallel_IO_interface
    I2C0 = 0x03  # I2C Serial interface – master 0
    I2C1 = 0x04  # I2C Serial interface – master 1
    I2C2 = 0x05  # I2C Serial interface – master 2
    I2C3 = 0x06  # I2C Serial interface – master 3
    I2C4 = 0x07  # I2C Serial interface – master 4
    I2C5 = 0x08  # I2C Serial interface – master 5
    I2C6 = 0x09  # I2C Serial interface – master 6
    I2C7 = 0x0A  # I2C Serial interface – master 7
    I2C8 = 0x0B  # I2C Serial interface – master 8
    I2C9 = 0x0C  # I2C Serial interface – master 9
    I2CA = 0x0D  # I2C Serial interface – master 10
    I2CB = 0x0E  # I2C Serial interface – master 11
    I2CC = 0x0F  # I2C Serial interface – master 12
    I2CD = 0x10  # I2C Serial interface – master 13
    I2CE = 0x11  # I2C Serial interface – master 14
    I2CF = 0x12  # I2C Serial interface – master 15

    SEU_Counter = 0x13  # Single Event Upset counter
    JTAG = 0x13  # JTAG serial master interface
    CTRL_Read_ID = 0x14  # Read chip ID
    ADC = 0x14  # Analog to digital converter (ADC)
    DAC = 0x15  # Digital to analog converter (DAC)


class CRBBits(IntEnum):
    """
    CRB - GBT-SCA Channel enable register B
    """
    ENSPI = 1  # SPI serial master interface enable flag
    ENGPIO = 2  # Parallel Input / Output interface enable flag
    ENI2C0 = 3  # I2C master interface number 0 enable flag
    ENI2C1 = 4  # I2C master interface number 1 enable flag
    ENI2C2 = 5  # I2C master interface number 2 enable flag
    ENI2C3 = 6  # I2C master interface number 3 enable flag
    ENI2C4 = 7  # I2C master interface number 4 enable flag
    W_OFFSET = 24
    R_OFFSET = 0


class CRCBits(IntEnum):
    """
    CRC - GBT-SCA Channel enable register C
    """
    ENI2C5 = 0  # I2C master interface number 5 enable flag
    ENI2C6 = 1  # I2C master interface number 6 enable flag
    ENI2C7 = 2  # I2C master interface number 7 enable flag
    ENI2C8 = 3  # I2C master interface number 8 enable flag
    ENI2C9 = 4  # I2C master interface number 9 enable flag
    ENI2CA = 5  # I2C master interface number 10 enable flag
    ENI2CB = 6  # I2C master interface number 11 enable flag
    ENI2CC = 7  # I2C master interface number 12 enable flag


class CRDBits(IntEnum):
    """
    CRD - GBT-SCA Channel enable register D
    """
    ENI2CD = 0  # I2C master interface number 13 enable flag
    ENI2CE = 1  # I2C master interface number 14 enable flag
    ENI2CF = 2  # I2C master interface number 15 enable flag
    ENJTAG = 3  # JTAG serial master interface enable flag
    ENADC0 = 4  # Analog to Digital converter enable flag eFuses/Serial Number reading
    ENDAC1 = 6  # Digital to Analog converter enable flag


class StatusRegisterBits(IntEnum):
    """
    I2C channel STATUS register
    """
    SUCC = 2  # This bit is set when the last I2C transaction was successfully executed.
    LEVERR = 3  # This bit is set to ‘1’ if the I2C master port finds that the SDA line is pulled low ‘0’ before
    # initiating a transaction. If this happens the I2C bus is probably broken. The bit represents the status of the
    # SDA line and cannot be reset.
    INVCOM = 5  # This bit is set if an invalid command was sent to the I2C channel. The bit is cleared by a channel
    # reset.
    NOACK = 6  # K This bit is set if the last operation has not been acknowledged by the I2C slave acknowledge.
    # This bit is set/reset at the end of each I2C transaction.


@unique
class DataRegisterBits(IntEnum):
    """
    I2C channel DATA register

    """
    BYTE0 = 0
    BYTE1 = 8
    BYTE2 = 16
    BYTE3 = 24
    BYTE4 = 32
    BYTE5 = 40
    BYTE6 = 48
    BYTE7 = 56
    BYTE8 = 64
    BYTE9 = 72
    BYTE10 = 80
    BYTE11 = 88
    BYTE12 = 96
    BYTE13 = 104
    BYTE14 = 112
    BYTE15 = 120


class SCAI2CConfigurationRegisters(Enum):
    """
    the registers defined in the I2C channel interface.
    """
    MASK = I2C_configuration_registers_properties_type(
        Mode=Operation.ReadWrite,
        Function='Mask register for read - modify - write operations'
    )
    CTRL = I2C_configuration_registers_properties_type(
        Mode=Operation.ReadWrite,
        Function='Control register'
    )
    STATUS = I2C_configuration_registers_properties_type(
        Mode=Operation.Read,
        Function='Status Register DATA'
    )
    DATA = I2C_configuration_registers_properties_type(
        Mode=Operation.ReadWrite,
        Function='Data register.Holds transmit or received buffers for multi - byte operations'
    )


def find_register(search):
    return [_ for _ in SCA_Register if search in _.value.Function_Description]


@unique
class SCA_Register(Enum):
    """
    SCA Register
    """
    CTRL_R_ID = Command_properties_type(
        Channel=0x14,
        CMD=0xD1,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Read the Chip ID '
    )
    CTRL_W_CRB = Command_properties_type(
        Channel=0x00,
        CMD=0x02,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='Write Control reg. B'
    )
    CTRL_W_CRC = Command_properties_type(
        Channel=0x00,
        CMD=0x04,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='Write Control reg. C'
    )
    CTRL_W_CRD = Command_properties_type(
        Channel=0x00,
        CMD=0x06,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='Write Control reg. D'
    )
    CTRL_R_CRB = Command_properties_type(
        Channel=0x00,
        CMD=0x03,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Read Control reg. B'
    )
    CTRL_R_CRC = Command_properties_type(
        Channel=0x00,
        CMD=0x05,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Read Control reg. C'
    )
    CTRL_R_CRD = Command_properties_type(
        Channel=0x00,
        CMD=0x07,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Read Control reg. D'
    )
    CTRL_R_SEU = Command_properties_type(
        Channel=0x13,
        CMD=0xF1,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Read the SEU counter'
    )
    CTRL_C_SEU = Command_properties_type(
        Channel=0x13,
        CMD=0xF0,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='Reset the SEU counter'
    )

    I2C_RMW_XOR = Command_properties_type(
        Channel=0,
        CMD=0xCA,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2CAtomic Read modify write XOR'
    )

    I2C_W_CTRL = Command_properties_type(
        Channel=0,
        CMD=0x30,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write CONTROL register'
    )

    I2C_R_CTRL = Command_properties_type(
        Channel=0,
        CMD=0x31,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read CONTROL register'
    )

    I2C_R_STR = Command_properties_type(
        Channel=0,
        CMD=0x11,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read STATUS register'
    )

    I2C_W_MSK = Command_properties_type(
        Channel=0,
        CMD=0x20,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write MASK register'
    )

    I2C_R_MSK = Command_properties_type(
        Channel=0,
        CMD=0x21,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read MASK register'
    )

    I2C_W_DATA0 = Command_properties_type(
        Channel=0,
        CMD=0x40,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write data register bytes 0,1,2,3'
    )

    I2C_R_DATA0 = Command_properties_type(
        Channel=0,
        CMD=0x41,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read data register bytes 0,1,2,3'
    )

    I2C_W_DATA1 = Command_properties_type(
        Channel=0,
        CMD=0x50,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write data register bytes 4,5,6,7'
    )

    I2C_R_DATA1 = Command_properties_type(
        Channel=0,
        CMD=0x51,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read data register bytes 4,5,6,7'
    )
    I2C_W_DATA2 = Command_properties_type(
        Channel=0,
        CMD=0x60,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write data register bytes 8,9,10,11'
    )

    I2C_R_DATA2 = Command_properties_type(
        Channel=0,
        CMD=0x61,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read data register bytes 8,9,10,11'
    )

    I2C_W_DATA3 = Command_properties_type(
        Channel=0,
        CMD=0x70,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Write data register bytes 12,13,14,15'
    )

    I2C_R_DATA3 = Command_properties_type(
        Channel=0,
        CMD=0x71,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Read data register bytes 12,13,14,15'
    )

    I2C_S_7B_W = Command_properties_type(
        Channel=0,
        CMD=0x82,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Start I2C single byte write transaction using 7-bits address'
    )

    I2C_S_7B_R = Command_properties_type(
        Channel=0,
        CMD=0x86,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Start I2C single byte Read transaction using 7-bits address'
    )

    I2C_S_10B_W = Command_properties_type(
        Channel=0,
        CMD=0x8A,
        Length=4,
        Offset=8,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Start I2C single byte write transaction using 10-bits address'
    )

    I2C_S_10B_R = Command_properties_type(
        Channel=0,
        CMD=0x8E,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Start I2C single byte read transaction using 10-bits address'
    )

    I2C_M_7B_W = Command_properties_type(
        Channel=0,
        CMD=0xDA,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Start I2C multi byte write transaction using 7-bits address'
    )

    I2C_M_7B_R = Command_properties_type(
        Channel=0,
        CMD=0xDE,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Start I2C multi byte read transaction using 7-bits address'
    )

    I2C_M_10B_W = Command_properties_type(
        Channel=0,
        CMD=0xE2,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Start I2C multi byte write transaction using 10-bits address'
    )

    I2C_M_10B_R = Command_properties_type(
        Channel=0,
        CMD=0xE6,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Function_Description='I2C Start I2C multi byte read transaction using 10-bits address'
    )

    '''
    I2C_RMW_AND = Command_properties_type(

            #CMD=0x,
            Length=4,
            Offset=16,
            Data=0x00,
            Operation=Operation.Write,
            Function_Description='I2C Read modify write atomic operation'
        )
        '''
    I2C_RMW_OR = Command_properties_type(
        Channel=0,
        CMD=0xC6,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Function_Description='I2C Atomic Read modify write OR'
    )
