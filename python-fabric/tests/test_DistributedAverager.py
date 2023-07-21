import os
import pathlib
import queue
import time

import watchdog
import watchdog.observers

from app_test_suite import FileSystemEventHandlerWatchdog
import app_test_suite


class AppSpec:
    def __init__(self, expected_peer_count, peer_start_timeout_seconds):
        self.files = {}
        self.expected_peer_count = expected_peer_count
        self.init_time = time.time()
        self.peer_required_start_time = 30  # not used
        self.peer_required_start_time = self.init_time + peer_start_timeout_seconds

    def callback(self, event_source):
        if ".log" not in event_source:
            return False, "Source is not a log file"

        print(f"Event source: {event_source}")
        file_name = os.path.basename(event_source)
        if file_name not in self.files:
            file_handle = open(event_source, "r")
            self.files[file_name] = {"handle": file_handle,
                                     "peers": []}
        else:
            file_handle = self.files[file_name]["handle"]

        for line in file_handle:
            print(f"file: {file_name}, line: {line}")

            if "peer" in line:
                peer_id = line.split(" ")[1]
                if peer_id not in self.files[file_name]["peers"]:
                    self.files[file_name]["peers"].append(peer_id)
                    # indicates that this client has been seen on the node that writes to this file

        peers_online, result = peers_are_online(self)
        # Termination condition
        finished = False
        if peers_online:
            finished = True
        else:
            if time.time() > self.peer_required_start_time:
                finished = True
                result = "Peer start timeout exceeded"

        return finished, result


def peers_are_online(app_spec):
    peers_online = True
    for file_name in app_spec.files:
        if len(app_spec.files[file_name]["peers"]) != app_spec.expected_peer_count:
            print(f"{file_name} is missing peers. "
                  f"Expected {app_spec.expected_peer_count}, found {len(app_spec.files[file_name]['peers'])}")
            peers_online = False
            break

    if peers_online:
        print(f"All peers online")
        return True, "All peers online"
    else:
        print(f"Peers not online")
        return False, "Peers not online yet"


def test_distributed_averager_app():
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
    app_name = "DistributedAverager"
    clients = ['172.21.20.40', '172.21.20.41', '172.21.20.43']

    # Launch the app
    c = app_test_suite.launch_riaps_app(
        app_folder_path="/home/riaps/projects/RIAPS/riaps-pycom/tests/DistributedAverager/",
        app_file_name="daver.riaps",
        depl_file_name="daver.depl",
        database_type="dht",
        required_clients=clients
    )

    # Create the app spec
    app_spec = AppSpec(expected_peer_count=len(clients)-1,  # 3 clients minus itself
                       peer_start_timeout_seconds=120)  # give the peers 2 minutes to start
    # expected_peer_count is not actually right, it should technically be derived from the deployment
    # and potentially the app file. But for now, this is fine.
    # Can make assert fail by setting the peer_start_timeout_seconds to 0

    # Watch the log file for changes via the event queue
    max_seconds_without_callback = 10
    result = app_test_suite.watch_riaps_app(event_q, app_spec, max_seconds_without_callback=max_seconds_without_callback)

    # Stop the app
    app_test_suite.terminate_riaps_app(c, app_name)
    # Stop the observer
    observer.stop()

    # Check criteria for successful test
    error_conditions = ["max_seconds_without_callback exceeded",
                        "Peer start timeout exceeded"]
    print(f"Test result: {result}")
    assert result not in error_conditions, f"Test failed: {result} "


