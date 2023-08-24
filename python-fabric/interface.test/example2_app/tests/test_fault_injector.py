import os
import pathlib
import pytest
import queue
import sys
import zmq

import watchdog
import watchdog.observers

sys.path.append('/home/riaps/projects/eiselesr/sandbox/python-fabric/interface.test/example2_app')

import test_suite.test_api as test_api
from test_suite.test_api import FileSystemEventHandlerWatchdog
from test_suite.test_spec import TestSpec
from test_suite.testInterface import Injector


class AppTestSpec(TestSpec):
    def __init__(self):
        super().__init__()

    def callback(self, event_source):
        super().callback(event_source)


def test_sanity():
    assert True


def test_app():
    # Set up the shared event queue
    event_q = queue.Queue()
    log_file_path = str(pathlib.Path(__file__).parents[1]) + "/server_logs"

    # Set up the event handler with the event queue
    file_event_handler = FileSystemEventHandlerWatchdog(event_q=event_q)

    # Set up the observer with the event handler
    observer = watchdog.observers.Observer()
    observer.schedule(file_event_handler, path=log_file_path, recursive=False)
    observer.start()

    # Set up the app
    app_name = "Demo"
    clients = ['172.21.20.50']

    # Launch the app
    c = test_api.launch_riaps_app(
        app_folder_path="/home/riaps/projects/eiselesr/sandbox/python-fabric/interface.test/example2_app",
        app_file_name="Demo_test.riaps",
        depl_file_name="Demo.depl",
        database_type="dht",
        required_clients=clients
    )

    # Create the app spec
    app_spec = AppTestSpec()

    # Watch the log file for changes via the event queue and check termination conditions
    # max_seconds_without_callback = 10
    # result = app_test_suite.watch_riaps_app(event_q, app_spec, max_seconds_without_callback=max_seconds_without_callback)

    input("Press enter when ready to inject fault: ")
    # Inject fault
    injector = Injector(ip="172.21.20.50")

    msg = {
        "function": "on_tick",
        "patch": "faulty_on_tick"
    }
    injector.send_request(msg)
    #
    input("Press enter when ready to revert fault: ")
    msg = {
        "function": "on_tick",
        "patch": "revert"
    }
    injector.send_request(msg)

    result = input("Press enter to terminate the app: ")

    # Stop the app
    test_api.terminate_riaps_app(c, app_name)
    # Stop the observer
    observer.stop()

    # Check criteria for successful test
    error_conditions = ["max_seconds_without_callback exceeded"]
    print(f"Test result: {result}")
    assert result not in error_conditions, f"Test failed: {result} "


