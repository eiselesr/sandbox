import abc
import os
import pathlib
import queue
import time
import watchdog.events
import watchdog.observers

from riaps.ctrl.ctrl import Controller as riaps_controller
from riaps.utils.config import Config as riaps_config


class EventHandler(abc.ABC):
    @abc.abstractmethod
    def write_event_q(self, event):
        pass


class FileSystemEventHandlerWatchdog(EventHandler, watchdog.events.FileSystemEventHandler):
    def __init__(self, event_q):
        self.event_q = event_q
        super().__init__()

    def on_any_event(self, event):
        pass
        # print(f"{event.event_type}, {event.src_path}")

    def on_modified(self, event):
        # print(f"on_modified: {event.src_path}")
        self.write_event_q(event)

    def write_event_q(self, event):
        self.event_q.put(f"{event.src_path}")

class FileObserver:
    def __init__(self, event_q, file_path):
        file_event_handler = FileSystemEventHandlerWatchdog(event_q=event_q)
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(file_event_handler, path=file_path, recursive=False)
        self.start()

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()



def launch_riaps_app(
        app_folder_path=str(pathlib.Path(__file__).parents[1]),
        app_file_name="app.riaps",
        depl_file_name="app.depl",
        database_type="dht",
        required_clients=None):
    the_config = riaps_config()
    c = riaps_controller(port=8888, script="-")

    app_folder_path = app_folder_path
    c.setAppFolder(app_folder_path)

    app_name_key = c.compileApplication(app_file_name, app_folder_path)
    deployment_file_name = depl_file_name
    c.compileDeployment(deployment_file_name)

    # start Database
    if database_type == "dht":
        c.startDht()
    elif database_type == "redis":
        c.startRedis()
    c.startService()

    # wait for clients to be discovered
    if required_clients is not None:
        known_clients = []
        while not set(required_clients).issubset(set(known_clients)):
            known_clients = c.getClients()
            print(f"known_clients: {known_clients}")
            time.sleep(1)

    # load application
    print(f"loading application: {app_name_key}")
    is_app_loaded = c.loadByName(app_name_key)
    print(f"is_app_loaded: {is_app_loaded}")
    assert is_app_loaded is True
    # launch application
    print(f"launching application: {app_name_key}")
    is_app_launched = c.launchByName(app_name_key)
    print(f"is_app_launched: {is_app_launched}")
    assert is_app_launched is True

    return c, app_name_key


def watch_riaps_app(event_q, app_spec, max_seconds_without_callback=10):
    files = {}
    finished = False
    time_of_last_callback = time.time()
    print("watching app")
    result = None
    while not finished:

        if time.time() - time_of_last_callback > max_seconds_without_callback:
            print("max_seconds_without_callback exceeded")
            return "max_seconds_without_callback exceeded"

        event_source = event_q.get()

        finished, result = app_spec.callback(event_source)
        time_of_last_callback = time.time()
    return result


def terminate_riaps_app(c, app_name):
    # Halt application
    print("Halt app")
    is_app_halted = c.haltByName(app_name)
    # haltByName (line 799).
    print(f"app halted? {is_app_halted}")

    # Remove application
    print("remove app")
    c.removeAppByName(app_name)  # has no return value.
    # removeAppByName (line 914).
    print("app removed")

    # Stop controller
    print("Stop controller")
    c.stop()
    print("controller stopped")



