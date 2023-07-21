import fabric
from fabric.group import SerialGroup, ThreadingGroup
import pathlib
import pytest
import queue
import time


@pytest.fixture(scope='module')
def remote_group():
    # Set the connection configurations
    config = fabric.Config(
        overrides={'connect_kwargs': {'key_filename': '/home/riaps/riaps_initial_keys/riaps_initial.key'}})

    # Create a list of host strings
    hosts = ['riaps@172.21.20.40', 'riaps@172.21.20.41', 'riaps@172.21.20.43']

    # Create a ThreadingGroup object for the hosts
    group = ThreadingGroup(*hosts, config=config)

    yield group

    # Close the connections after the tests
    group.close()


def test_run_command_on_remote_nodes(remote_group):
    results = remote_group.run('echo Hello, Fabric!', hide=True)
    for connection, result in results.items():
        print(f'connection: {connection}, result: {result}')
        assert result.stdout.strip() == 'Hello, Fabric!'