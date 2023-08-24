import abc
import inspect
import json
import logging
import threading
import time
import zmq


class Injector:
    def __init__(self, ip="172.21.20.70"):
        address = f"tcp://{ip}:5555"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        identity = b"Injector"  # Setting a unique identity for the DEALER socket
        self.socket.setsockopt(zmq.IDENTITY, identity)
        self.socket.connect(address)

    def send_request(self, request):
        print(f"Sending request: {request}")
        request_bytes = json.dumps(request).encode('utf-8')
        self.socket.send(request_bytes)

    def recv(self):
        reply = self.socket.recv()
        print(f"Received reply: {reply.decode()}")
        return reply

    def close(self):
        self.socket.close()
        self.context.term()


class InjectionServer(threading.Thread):
    def __init__(self, logger=None, handler=None, riaps_port=None):
        super().__init__()

        if logger is None:
            # If no logger is provided, use the basicConfig logger
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            # Use the provided logger
            self.logger = logger

        self.handler = handler
        if riaps_port:
            self.riaps_port = riaps_port
            self.riaps_plug = riaps_port.setupPlug(self)
            self.logger.debug(f"InjectionServer | riaps_plug: {self.riaps_plug} "
                              f"plug identity: {self.riaps_plug.identity}"
                              f"socket name: {riaps_port.instName}")
            # self.poller.register(self.riaps_plug, zmq.POLLIN)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind("tcp://*:5555")

    def run(self):
        self.logger.info("Server started. Listening for requests...")
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while True:
            self.logger.info(f"Waiting for messages...{time.time()}")
            events = dict(poller.poll(1000))
            if self.socket in events and events[self.socket] == zmq.POLLIN:
                identity, request_bytes = self.socket.recv_multipart()
                request = json.loads(request_bytes.decode('utf-8'))
                self.logger.info(f"Received request from client {identity}: {request}")
                if self.handler is not None:
                    self.handler(request["function"], request["patch"])
                if self.riaps_plug is not None:
                    self.riaps_plug.send_pyobj(request)

    def close(self):
        self.socket.close()
        self.context.term()


class TestInterface:
    def __init__(self, app, logger=None):

        self.app = app

        if not hasattr(self.app, "function_patches"):
            raise Exception("No function patches provided")

        if logger is None:
            # If no logger is provided, use the basicConfig logger
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            # Use the provided logger
            self.logger = logger

        # self.test_server_thread = InjectionServer(logger=self.logger,
        #                                           handler=self.patch_function)
        # self.test_server_thread.start()

    def revert_patch(self, function_name):
        original_function = getattr(self.app.__class__, function_name)
        setattr(self.app, function_name, original_function.__get__(self.app))

    def patch_function(self, function_name, new_function_name):

        if new_function_name == "revert":
            self.revert_patch(function_name)
            return

        self.logger.info(f"Received patch request for function {function_name} with {new_function_name}")
        original_function = getattr(self.app, function_name)
        new_function = self.app.function_patches[new_function_name]

        if not new_function:
            raise Exception(f"Function {new_function} not found")

        new_function = new_function.__get__(self.app)

        original_params = inspect.signature(original_function).parameters
        patched_params = inspect.signature(new_function).parameters

        if original_params == patched_params:
            self.logger.info("Patched function has the same parameters as the original function.")
            setattr(self.app, function_name, new_function)
        else:
            self.logger.info(
                f"{new_function_name} has {patched_params} while original {function_name} has {original_params}.")


"""
Code below is for demonstration/testing purposes only
"""


def run_server():
    server = InjectionServer()
    server.start()


def run_client():
    client = Injector()
    for request_number in range(5):
        request = {"request_number": request_number + 1}
        client.send_request(request)
        time.sleep(1)  # Add a small delay between each request for demonstration purposes


if __name__ == "__main__":
    import multiprocessing as mp

    server_process = mp.Process(target=run_server)
    client_process = mp.Process(target=run_client)

    server_process.start()
    client_process.start()

    server_process.join()
    client_process.join()
