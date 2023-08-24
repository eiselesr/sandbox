import abc
import os


class TestSpec:
    # def __init__(self, expected_peer_count, peer_start_timeout_seconds):
    def __init__(self):
        self.files = {}
        # self.expected_peer_count = expected_peer_count
        # self.init_time = time.time()
        # self.peer_required_start_time = 30  # not used
        # self.peer_required_start_time = self.init_time + peer_start_timeout_seconds

    @abc.abstractmethod
    def termination_logic(self, file_handle):
        finished = False
        result = None
        for line in file_handle:
            print(f"file name: {file_handle.name}, line: {line}")
            if "Hello World" in line:
                finished = True
                result = None
        return finished, result

    def callback(self, event_source):
        if ".log" not in event_source:
            return False, "Source is not a log file"

        # print(f"Event source: {event_source}")
        file_name = os.path.basename(event_source)
        if file_name not in self.files:
            file_handle = open(event_source, "r")
            self.files[file_name] = {"handle": file_handle,
                                     "peers": []}
        else:
            file_handle = self.files[file_name]["handle"]

        # Termination logic
        finished, result = self.termination_logic(file_handle)
        return finished, result
