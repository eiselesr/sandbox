import logging
import os
import pulsar
import threading


class Shim:
    def __init__(self, func):
        print(f"id of function: {id(func)}")
        self.messages_received = threading.Event()
        self.app_function = func
        self.client = pulsar.Client('pulsar://localhost:6650')
        self.consumer = self.client.subscribe('my-topic',
                                              'my-subscription',
                                              message_listener=self.shim_function)

        self.cleanup_channel = self.client.subscribe('cleanup-topic',
                                                     'cleanup-subscription',
                                                     message_listener=self.cleanup)
        self.messages_received.wait()

    def cleanup(self, consumer, msg):
        self.messages_received.set()

    def shim_function(self, consumer, msg):
        self.app_function(msg)
        consumer.acknowledge_cumulative(msg)

    def close(self):
        self.client.close()


