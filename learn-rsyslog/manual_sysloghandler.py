import logging
import logging.handlers
import socket


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

f = logging.Formatter("%(module)s:[%(filename)s line:%(lineno)d]: msg: %(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# slh = logging.handlers.SysLogHandler(address=("localhost", 514), 
#                                    facility="syslog",
#                                    socktype=socket.SOCK_STREAM)

slh = logging.handlers.SysLogHandler(address="/dev/log",
                                     facility="syslog")

slh.setLevel(logging.DEBUG)

ch.setFormatter(f)
slh.setFormatter(f)
logger.addHandler(ch)
logger.addHandler(slh)


logger.info("Manual logger test")