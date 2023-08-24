import fabric
import fabric.exceptions
from fabric.group import SerialGroup, ThreadingGroup
from paramiko import SSHException
import pathlib
import pytest
import queue
import time


def rsync_put(c, local_path, remote_host, remote_path):
    c.local(f"rsync -avz {local_path} {remote_host}:{remote_path}")


def tmux_run(tmux_command):
    results = remote_group.run(tmux_command, hide=True)

    for connection, result in results.items():
        print(f'connection: {connection}, command: {tmux_command}, result: {result}')


def run_command_with_retry(connection, command, max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            result = connection.run(command)
            return result
        except Exception as e:
            print(f"Command execution failed: {e}")
            retries += 1
            time.sleep(retry_delay)
            # Reestablish the connection
            try:
                print(f"Reestablishing connection to {connection.host}")
                connection.close()
            except:
                pass
            connection.open()

    raise Exception("Failed to run the command after multiple retries")


@pytest.fixture(scope='module')
def remote_group():
    # Set the connection configurations
    config = fabric.Config(
        overrides={'connect_kwargs': {'key_filename': '/home/riaps/riaps_initial_keys/riaps_initial.key'}})

    # Create a list of host strings
    hosts = ['riaps@172.21.20.41']
    # hosts = ['riaps@172.21.20.40', 'riaps@172.21.20.41', 'riaps@172.21.20.43']

    # Create a ThreadingGroup object for the hosts
    group = ThreadingGroup(*hosts, config=config)

    yield group

    # Close the connections after the tests
    group.close()


@pytest.fixture(scope='module')
def test_setup(remote_group):
    # The local path to the Python script containing the function
    local_script_path = "tests/fmlib"

    # The remote path where the script will be copied to
    remote_script_path = "/home/riaps/tmp_remote_pytest"

    # Transfer the local script to the remote server
    for connection in remote_group:
        print(f'connection: {connection}, host: {connection.host}')
        rsync_put(connection, local_script_path, connection.host, remote_script_path)
        print(f'connection: {connection}')

    # The name of the tmux session to create
    session_name = "my_session"
    window_name = "main"

    # Command to create a new tmux session
    command = f"tmux new-session -d -s {session_name} -n {window_name}"
    remote_group.run(command, hide=True)

    yield remote_group, remote_script_path, session_name, window_name

    # Close the tmux session after the tests
    try:
        tmux_command = f"tmux kill-session -t {session_name}"
        results = remote_group.run(tmux_command, hide=True)

        for connection, result in results.items():
            print(f'connection: {connection}, command: {tmux_command}, result: {result}')
    except Exception as e:
        print(f"Encountered exception while closing tmux session: {e}")


def test_run_command_on_remote_nodes(remote_group):
    results = remote_group.run('echo Hello, Fabric!', hide=True)
    for connection, result in results.items():
        print(f'connection: {connection}, result: {result}')
        assert result.stdout.strip() == 'Hello, Fabric!'


def test_ip_link_down(remote_group, test_setup):

    remote_group, remote_script_path, session_name, window_name = test_setup

    # The name of the Python function to be called
    function_name = "network_interface_down"

    # Command to run the Python script from within the tmux session
    python_command = f'python3 {remote_script_path}/fmlib/faults.py -f {function_name}'
    tmux_command = f"tmux send-keys -t {session_name} '{python_command}' Enter"
    results = remote_group.run(tmux_command, hide=True)

    for connection, result in results.items():
        print(f'connection: {connection}, command: {function_name}, result: {result}')

    # Test termination conditions
    notable_events = ["calling function"]
    termination_events = ["network interface up"]
    finished = False

    # Command to capture the output of the tmux session
    tmux_command = f"tmux capture-pane -p -t '{window_name}.0' -S -"
    # Wait for the termination event to occur
    while not finished:
        print(f"tmux_command: {tmux_command}")
        results = remote_group.run(tmux_command, hide=True)

        for connection, result in results.items():
            print(f'connection: {connection}')
            for line in result.stdout.splitlines():
                if any(event in line for event in termination_events):
                    print(f'line: {line}')
                    finished = True
                if any(event in line for event in notable_events):
                    print(f'line: {line}')
        if not finished:
            print(f"sleeping for 5 seconds")
            time.sleep(5)


def test_power_failure(remote_group, test_setup):
    remote_group, remote_script_path, session_name, window_name = test_setup
    # The name of the Python function to be called
    function_name = "simulate_power_failure"

    python_command = f'sudo python3 {remote_script_path}/fmlib/faults.py -f {function_name}'
    tmux_command = f"tmux send-keys -t {session_name} '{python_command}' Enter"
    results = remote_group.run(tmux_command, hide=True)

    for connection, result in results.items():
        print(f'connection: {connection}, command: {tmux_command}, result: {result}')

    # Test termination conditions

    finished = False
    command = "uptime"
    while not finished:
        print(f"command: {tmux_command}")
        results = remote_group.run(command)
        print(f"results: {results}")
        i = input("Enter to continue")

        for c in remote_group:
            run_command_with_retry(c, command)
        finished = True









