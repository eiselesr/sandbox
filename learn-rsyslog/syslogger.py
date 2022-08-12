import logging
import logging.config
import socket
from pyrsistent import l
import yaml

# if using log.conf: 
# logging.socket = socket
# logging.config.fileConfig(...)
# del logging.socket

logconf = 'log.yaml'
with open(logconf, "r") as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
print(logger.name)
print(logger.handlers)
h = logger.handlers[1]
print(h.address)

def log_msg():
    logger = logging.getLogger(__name__)
    logger.info("test 2 syslogger from python")

log_msg()