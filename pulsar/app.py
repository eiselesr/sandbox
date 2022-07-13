import shim
import threading


class App:
    def __init__(self):
        self.msg_count = 0
        print(f"id of function: {id(self.app_function)}")

        self.pulsar_client = shim.Shim(self.app_function)

    def app_function(self, msg):
        self.msg_count += 1
        print(f"Received message {msg.data()} "
              f"id={msg.message_id()} "
              f"msg_count={self.msg_count}")


if __name__ == '__main__':
    a = App()



