import logging
import os
import pulsar


class Shim:
    def __init__(self, func):
        print(f"id of function: {id(func)}")
        self.client = pulsar.Client('pulsar://localhost:6650')
        self.consumer = self.client.subscribe('my-topic',
                                              'my-subscription',
                                              message_listener=func)

    def close(self):
        self.client.close()


