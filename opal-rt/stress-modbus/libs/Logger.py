import time
import functools
import spdlog as spd
import pickle

def nextTag(t):
    return t + 1

def pack(tag, pyobj):
    return (tag, pyobj)

def unpack(msg):
    return msg[0], msg[1]

def pack_bytes(tag, bytes_obj):
    theTuple = (tag,bytes_obj)
    return pickle.dumps(theTuple)

def unpack_bytes(msg):
    return pickle.loads(msg)

class EventLogger:
    def __init__(self, name):
        name = name
        self.logger = spd.FileLogger(f'compLog_{name}', 'logs/log_'+name)
        self.logger.set_pattern(pattern='%v')
        self.counter = 0

    def info(self, msg: str, timestamp=None):
        ts = timestamp or time.time()
        self.logger.info(f"{ts}::{msg}")
        self.logger.flush()

    def new_trace(self, msg, timestamp=None):
        ts = timestamp or time.time()
        self.counter += 1 
        self.info(f"{self.counter}::{msg}", ts)
        return self.counter

    def tracepoint(self, tag, msg, timestamp=None):
        ts = timestamp or time.time()
        self.info(f"{tag}::{msg}",ts)
        # return nextTag(tag)
        return tag
    
    def flush(self):
        self.logger.flush()
        