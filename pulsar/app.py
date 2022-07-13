import shim

import pulsar
import time
import threading


class App:
    def __init__(self):
        self.active = True
        self.msg_count = 0
        print(f"id of function: {id(self.app_function)}")

        self.pulsar_client = shim.Shim(self.app_function)

        self.messages_received = threading.Event()

    def app_function(self, consumer, msg):
        self.msg_count += 1
        print(f"Received message {msg.data()} "
              f"id={msg.message_id()} "
              f"msg_count={self.msg_count}")
        # Acknowledge successful processing of the message
        consumer.acknowledge_cumulative(msg)
        if self.msg_count >= 10:
            # a.active = False
            a.messages_received.set()


if __name__ == '__main__':
    a = App()

    a.messages_received.wait()

