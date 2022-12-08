from enum import Enum, IntEnum, unique
from collections import namedtuple

class Indicators:
    INFO = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'


Command_properties_type = namedtuple('Command_properties_type',
                                     'Channel CMD Length, Operation Offset Data Description')
I2C_configuration_registers_properties_type = namedtuple('I2C_configuration_registers_properties_type',
                                                         'Mode Function')
Enable_channel_properties_type = namedtuple('Enable_channel_properties_type', 'Register Bit')


WORD_LENGTH = 4


class Operation(IntEnum):
    Read = 0
    Write = 1
    ReadWrite = 2

ErrorFlags = { 0 : "Generic error flag",
               1 : "Invalid channel request",
               2 : "Invalid command request",
               3 : "Invalid transaction number request",
               4 : "Invalid length",
               5 : "Channel not enabled",
               6 : "Channel currently busy",
               7 : "Command in treatment"} 
         
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
    JTAG = 0x13  # JTAG serial master interface
    ADC = 0x14  # Analog to digital converter (ADC)
    DAC = 0x15  # Digital to analog converter (DAC)


def channel_id(channel_str: str):
    assert channel_str in [_.name for _ in Channel], f' There is no channel with name {channel_str}'
    return eval(f'Channel.{channel_str}.value')


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


class SPIControlRegisterBits(IntEnum):
    LEN = 1  # Represents how many bits to transmit during the following transmission. It can assume values from 0 to
    #          127 (value ‘0’ represents 128 bits)
    INVSCLK = 7  # Invert the SCLK level during inactivity time.
    #               INVSCLK = 0 -> SCLK idle level is low
    #               INVSCLK = 1 -> SCLK idle level is high
    GO_BUSY = 8  # Alternative method for starting the SPI transmission/Busy flag. Deprecated in SCA V2.
    #               The use of this method is not suggested, please write always value 0 to this bit.
    RXEDGE = 9  # Define the SCLK sampling edge of the MISO input line
    #             RXEDGE = 0 -> MISO signal is sampled on the rising edge of SCLK
    #             RXEDGE = 1 -> MISO signal is sampled on the falling edge of SCLK
    TXEDGE = 10  # Define the SCLK transmit edge of the MOSI output line
    #               TXEDGE = 0 -> MOSI signal change on the rising edge of SCLK
    #               TXEDGE = 1 -> MOSI signal change on the falling edge of SCLK
    MSB_LSB = 11  # Define the transmit order of the bits in the transmit FIFO and the position of the
    #               received bit in the received FIFO
    #               MSB/LSB = 0 -> Bits are transmitted from the most significant to the least significant
    #               MSB/LSB = 1 -> Bits are transmitted from the least significant to the most significant
    IE = 12  # Interrupt enable. Deprecated in SCA-V2. Please always write 1 in this bit.
    #               SSMODE = 13 Define if the Slave Select output signal is automatic or manually controlled.
    #               SSMODE = 1 -> When the GO command is sent, the slave select line (chosen with the
    #               SLAVESELECT register) is enabled at the beginning of the transmission
    #               and disabled at the end of the transmission.
    #               SSMODE = 0 -> The slave select pads are manually controlled. Any write operation on the
    #               SLAVESELECT register, toggle immediately the corresponding slave select
    #               pads.
    #               See SLAVE SELECT register for more information.


class JTAGControlRegisterBits(IntEnum):
    LEN = 1  # Number of bits transmitted in the single JTAG operation.
    #          It can assume values from 0 to  127 (value ‘0’ represents 128 bits)
    GO_BUSY = 8  # SCA-V2 -> Busy flag. JTAG bus operation currently going. Write operation not influent.
    #              SCA-V1 -> Alternative method for starting the JTAG transmission. Replaced with the
    #              JTAG_GO_M command in SCA-V2.
    RXEDGE = 9  # Define the TCK sampling edge of the TDI input line
    #             RXEDGE = 0 -> TDI signal is sampled on the rising edge of TCK (STANDARD)
    #             RXEDGE = 1 -> TDI signal is sampled on the falling edge of TCK
    TXEDGE = 10  # Define the TCK transmit edge of the TDO and TMS output lines
    #               TXEDGE = 0 -> TDO and TMS signal change on the rising edge of TCK (STANDARD)
    #               TXEDGE = 1 -> TDO and TMS signal change on the falling edge of TCK
    MSB_LSB = 11  # Define the transmit order of the bits in the transmit FIFO and the position of the
    #               received bit in the received FIFO
    #               MSB/LSB = 0 -> Bits are transmitted from the most significant to the least significant
    #               MSB/LSB = 1 -> Bits are transmitted from the least significant to the most significant
    INVTCK = 14  # Invert the TCK signal
    #                INVSCLK = 0 -> TCK idle level is high (STANDARD)
    #                INVSCLK = 1 -> TCK idle level is low
    ARESET = 16  # Asynchronous reset enable. Implemented only in SCA-V1.
    #                 In SCA-V2 the functionality of this bit is replaced with the JTAG_RESET command.

class Enable_from_Control_Reg(Enum):
    """
    Channels to enable from a control register
    """
    ENSPI = Enable_channel_properties_type(
        Register="CRB",
        Bit=1
    )
    ENGPIO = Enable_channel_properties_type(
        Register="CRB",
        Bit=2
    )
    ENI2C0 = Enable_channel_properties_type(
        Register="CRB",
        Bit=3
    )
    ENI2C1 = Enable_channel_properties_type(
        Register="CRB",
        Bit=4
    )
    ENI2C2 = Enable_channel_properties_type(
        Register="CRB",
        Bit=5
    )
    ENI2C3 = Enable_channel_properties_type(
        Register="CRB",
        Bit=6
    )
    ENI2C4 = Enable_channel_properties_type(
        Register="CRB",
        Bit=7
    )
    ENI2C5 = Enable_channel_properties_type(
        Register="CRC",
        Bit=0
    )
    ENI2C6 = Enable_channel_properties_type(
        Register="CRC",
        Bit=1
    )
    ENI2C7 = Enable_channel_properties_type(
        Register="CRC",
        Bit=2
    )
    ENI2C8 = Enable_channel_properties_type(
        Register="CRC",
        Bit=3
    )
    ENI2C9 = Enable_channel_properties_type(
        Register="CRC",
        Bit=4
    )
    ENI2CA = Enable_channel_properties_type(
        Register="CRC",
        Bit=5
    )
    ENI2CB = Enable_channel_properties_type(
        Register="CRC",
        Bit=6
    )
    ENI2CC = Enable_channel_properties_type(
        Register="CRC",
        Bit=7
    )
    ENI2CD = Enable_channel_properties_type(
        Register="CRD",
        Bit=0
    )
    ENI2CE = Enable_channel_properties_type(
        Register="CRD",
        Bit=1
    )
    ENI2CF = Enable_channel_properties_type(
        Register="CRD",
        Bit=2
    )
    ENJTAG = Enable_channel_properties_type(
        Register="CRD",
        Bit=3
    )
    ENADC = Enable_channel_properties_type(
        Register="CRD",
        Bit=4
    )
    ENDAC = Enable_channel_properties_type(
        Register="CRD",
        Bit=6
    )


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
        Description='Read the Chip ID '
    )
    CTRL_W_CRB = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x02,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='Write Control reg. B'
    )
    CTRL_W_CRC = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x04,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='Write Control reg. C'
    )
    CTRL_W_CRD = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x06,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='Write Control reg. D'
    )
    CTRL_R_CRB = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x03,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='Read Control reg. B'
    )
    CTRL_R_CRC = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x05,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='Read Control reg. C'
    )
    CTRL_R_CRD = Command_properties_type(
        Channel=Channel.CTRL.value,
        CMD=0x07,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='Read Control reg. D'
    )
    CTRL_R_SEU = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0xF1,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='Read the SEU counter'
    )
    CTRL_C_SEU = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0xF0,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='Reset the SEU counter'
    )

    # ------ I2C ------

    I2C_RMW_XOR = Command_properties_type(
        Channel=0,
        CMD=0xCA,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2CAtomic Read modify write XOR'
    )

    I2C_W_CTRL = Command_properties_type(
        Channel=0,
        CMD=0x30,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write CONTROL register'
    )

    I2C_R_CTRL = Command_properties_type(
        Channel=0,
        CMD=0x31,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read CONTROL register'
    )

    I2C_R_STR = Command_properties_type(
        Channel=0,
        CMD=0x11,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read STATUS register'
    )

    I2C_W_MSK = Command_properties_type(
        Channel=0,
        CMD=0x20,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write MASK register'
    )

    I2C_R_MSK = Command_properties_type(
        Channel=0,
        CMD=0x21,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read MASK register'
    )

    I2C_W_DATA0 = Command_properties_type(
        Channel=0,
        CMD=0x40,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write data register bytes 0,1,2,3'
    )

    I2C_R_DATA0 = Command_properties_type(
        Channel=0,
        CMD=0x41,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read data register bytes 0,1,2,3'
    )

    I2C_W_DATA1 = Command_properties_type(
        Channel=0,
        CMD=0x50,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write data register bytes 4,5,6,7'
    )

    I2C_R_DATA1 = Command_properties_type(
        Channel=0,
        CMD=0x51,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read data register bytes 4,5,6,7'
    )
    I2C_W_DATA2 = Command_properties_type(
        Channel=0,
        CMD=0x60,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write data register bytes 8,9,10,11'
    )

    I2C_R_DATA2 = Command_properties_type(
        Channel=0,
        CMD=0x61,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read data register bytes 8,9,10,11'
    )

    I2C_W_DATA3 = Command_properties_type(
        Channel=0,
        CMD=0x70,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Write data register bytes 12,13,14,15'
    )

    I2C_R_DATA3 = Command_properties_type(
        Channel=0,
        CMD=0x71,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Read data register bytes 12,13,14,15'
    )

    I2C_S_7B_W = Command_properties_type(
        Channel=0,
        CMD=0x82,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Start I2C single byte write transaction using 7-bits address'
    )

    I2C_S_7B_R = Command_properties_type(
        Channel=0,
        CMD=0x86,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Start I2C single byte Read transaction using 7-bits address'
    )

    I2C_S_10B_W = Command_properties_type(
        Channel=0,
        CMD=0x8A,
        Length=4,
        Offset=8,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Start I2C single byte write transaction using 10-bits address'
    )

    I2C_S_10B_R = Command_properties_type(
        Channel=0,
        CMD=0x8E,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Start I2C single byte read transaction using 10-bits address'
    )

    I2C_M_7B_W = Command_properties_type(
        Channel=0,
        CMD=0xDA,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Start I2C multi byte write transaction using 7-bits address'
    )

    I2C_M_7B_R = Command_properties_type(
        Channel=0,
        CMD=0xDE,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Start I2C multi byte read transaction using 7-bits address'
    )

    I2C_M_10B_W = Command_properties_type(
        Channel=0,
        CMD=0xE2,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Start I2C multi byte write transaction using 10-bits address'
    )

    I2C_M_10B_R = Command_properties_type(
        Channel=0,
        CMD=0xE6,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Read,
        Description='I2C Start I2C multi byte read transaction using 10-bits address'
    )

    '''
    I2C_RMW_AND = Command_properties_type(

            #CMD=0x,
            Length=4,
            Offset=16,
            Data=0x00,
            Operation=Operation.Write,
            Description='I2C Read modify write atomic operation'
        )
        '''
    I2C_RMW_OR = Command_properties_type(
        Channel=0,
        CMD=0xC6,
        Length=4,
        Offset=16,
        Data=0x00,
        Operation=Operation.Write,
        Description='I2C Atomic Read modify write OR'
    )

    # ------ SPI ------

    SPI_W_CTRL = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x40,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write CONTROL register'
    )

    SPI_R_CTRL = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x41,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read CONTROL register'
    )

    SPI_W_FREQ = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x50,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write frequency divider register'
    )

    SPI_R_FREQ = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x51,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read frequency divider register'
    )

    SPI_W_SS = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x60,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write slave select register'
    )

    SPI_R_SS = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x61,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read slave select register'
    )

    SPI_W_MOSI0 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x00,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write MOSI DATA buffer Bits [31:0]'
    )

    SPI_R_MISO0 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x01,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read MOSI DATA buffer Bits [31:0]'
    )

    SPI_W_MOSI1 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x10,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write MOSI DATA buffer Bits [63:32]'
    )

    SPI_R_MOSI1 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x11,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read MOSI DATA buffer Bits [63:32]'
    )

    SPI_W_MOSI2 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x20,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write MOSI DATA buffer Bits [95:64]'
    )

    SPI_R_MISO2 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x21,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read MOSI DATA buffer Bits [95:64]'
    )

    SPI_W_MOSI3 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x30,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='SPI Write MOSI DATA buffer Bits [95:64]'
    )

    SPI_R_MISO3 = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x31,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='SPI Read MOSI DATA buffer Bits [95:64]'
    )

    SPI_GO = Command_properties_type(
        Channel=Channel.SPI.value,
        CMD=0x72,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='Start SPI transaction'
    )

    # ------ JTAG ------

    JTAG_W_CTRL = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x80,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write CONTROL register'
    )

    JTAG_R_CTRL = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x81,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read CONTROL register'
    )

    JTAG_W_FREQ = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x90,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write frequency divider register'
    )

    JTAG_R_FREQ = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x91,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read divider register'
    )

    JTAG_W_TDO0 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x00,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TDO DATA Bits [31:0]'
    )

    JTAG_R_TDI0 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x01,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TDO DATA Bits [31:0]'
    )

    JTAG_W_TDO1 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x10,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TDO DATA Bits [63:32]'
    )

    JTAG_R_TDI1 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x11,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TDO DATA Bits [63:32]'
    )

    JTAG_W_TDO2 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x20,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TDO DATA Bits [95:64]'
    )

    JTAG_R_TDI2 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x21,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TDO DATA Bits [95:64]'
    )

    JTAG_W_TDO3 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x30,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TDO DATA Bits [127:96]'
    )

    JTAG_R_TDI3 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x31,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TDO DATA Bits [127:96]'
    )

    JTAG_W_TMS0 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x40,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TMS DATA Bits [31:0]'
    )

    JTAG_R_TMS0 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x41,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TMS DATA Bits [31:0]'
    )

    JTAG_W_TMS1 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x50,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TMS DATA Bits [63:32]'
    )

    JTAG_R_TMS1 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x51,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TMS DATA Bits [63:32]'
    )

    JTAG_W_TMS2 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x60,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TMS DATA Bits [95:64]'
    )

    JTAG_R_TMS2 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x61,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TMS DATA Bits [95:64]'
    )

    JTAG_W_TMS3 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x70,
        Length=6,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='JTAG Write TMS DATA Bits [31:0]'
    )

    JTAG_R_TMS3 = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x71,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='JTAG Read TMS DATA Bits  [127:96]'
    )

    JTAG_ARESET = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0xC0,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='Send RESET pulse'
    )

    JTAG_GO = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0xA2,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='Start transmission'
    )

    JTAG_GO_M = Command_properties_type(
        Channel=Channel.JTAG.value,
        CMD=0x80,
        Length=2,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='Start transmission'
    )

    # ------ GPIO ------

    GPIO_W_DATAOUT = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x10,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register DATAOUT'
    )

    GPIO_R_DATAOUT = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x11,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register DATAOUT'
    )

    GPIO_R_DATAIN = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x01,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register DATAIN'
    )

    GPIO_W_DIRECTION = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x20,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register DIRECTION'
    )

    GPIO_R_DIRECTION = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x21,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register DIRECTION'
    )

    GPIO_W_INTENABLE = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x60,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register INTENABLE'
    )

    GPIO_R_INTENABLE = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x61,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register INTENABLE'
    )

    GPIO_W_INTSEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x30,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register INTSEL'
    )

    GPIO_R_INTSEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x31,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register INTSEL'
    )

    GPIO_W_INTTRIG = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x40,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register INTTRIG'
    )

    GPIO_R_INTTRIG = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x41,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register INTTRIG'
    )

    GPIO_W_INTS = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x70,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register INTS'
    )

    GPIO_R_INTS = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x71,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register INTS'
    )

    GPIO_W_CLKSEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x80,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register CLKSEL'
    )

    GPIO_R_CLKSEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x81,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register CLKSEL'
    )

    GPIO_W_EDGESEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x90,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='GPIO Write register EDGESEL'
    )

    GPIO_R_EDGESEL = Command_properties_type(
        Channel=Channel.GPIO.value,
        CMD=0x91,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='GPIO Read register EDGESEL'
    )

    # ------ DAC ------

    DAC_W_A = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x10,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='DAC Set value on output A'
    )

    DAC_R_A = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x11,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='DAC Read the value of output A'
    )

    DAC_W_B = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x20,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='DAC Set value on output B'
    )

    DAC_R_B = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x21,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='DAC Read the value of output B'
    )

    DAC_W_C = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x30,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='DAC Set value on output C'
    )

    DAC_R_C = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x31,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='DAC Read the value of output C'
    )

    DAC_W_D = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x40,
        Length=4,
        Offset=24,
        Data=0x00,
        Operation=Operation.Write,
        Description='DAC Set value on output D'
    )

    DAC_R_D = Command_properties_type(
        Channel=Channel.DAC.value,
        CMD=0x41,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='DAC Read the value of output D'
    )

    # ------ ADC ------

    ADC_GO = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x02,
        Length=4,
        Offset=0,
        Data=0x01,
        Operation=Operation.Write,
        Description='ADC Start of conversion'
    )

    ADC_W_MUX = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x50,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='ADC Write register INSEL'
    )

    ADC_R_MUX = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x50,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='ADC Read register INSEL'
    )

    ADC_W_CURR = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x60,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='ADC Write register'
    )

    ADC_R_CURR = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x61,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='ADC Read register'
    )

    ADC_W_GAIN = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x10,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Write,
        Description='ADC Set value on output A'
    )

    ADC_R_GAIN = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x11,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='ADC Read the value of output A'
    )

    ADC_R_DATA = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x21,
        Length=4,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description='command allows to read the value of the latest conversion.'
    )

    ADC_R_RAW = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x31,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description="command allows to read the raw value of the conversion, therefore without any offset or gain "
                    "correction. "
    )

    ADC_R_OFS = Command_properties_type(
        Channel=Channel.ADC.value,
        CMD=0x41,
        Length=1,
        Offset=0,
        Data=0x00,
        Operation=Operation.Read,
        Description="command allows to read the value of the offset evaluated during the latest conversion"
    )
