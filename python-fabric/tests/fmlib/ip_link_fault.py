import time

import faults

faults.network_interface_down()
time.sleep(20)
faults.network_interface_up()
