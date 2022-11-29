import emp
import time 
import uhal 

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
uhal.setLogLevelTo(uhal.LogLevel.WARNING)

from lpgbt_control_lib import LpgbtV1
from lpgbt_control_lib.lpgbt import lpgbt_accessor
from chip import Chip

test_word = [1,2,3,4,5,6,7,9,10,11]
test_instance = Chip()
path = "~/lpgbt_v1_3_ceacmsfw_221102_1333/hls_connections.xml"
fpga = "x0"
link = 6

test_instance.hw_interface(path, fpga, link)
test_hw = test_instance.emp_cont.hw()
test_hw.getNode("payload.TST_RAM").writeBlock(test_word)
test_hw.dispatch()
#read_val = test_hw.getNode("info.source_areas").readBlock(4)
read_val = test_hw.getNode("payload.TST_RAM").readBlock(50)
test_hw.dispatch()
print(read_val)

