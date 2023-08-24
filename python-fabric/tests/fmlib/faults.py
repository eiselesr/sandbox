# 
# Fault simulation
#

import ctypes
import os
import time
# import libtmux as tmux


def exit():
    """
    process exit
    """
    os._exit(0)


def crash():
    """
    process crash
    """
    ctypes.string_at(0)


def kill(s):
    """
    process kill
    """
    os.system("pkill -SIGKILL -f %s" % s)


def panic():
    """
    kernel panic - use with extreme care
    """
    os.system('sync')
    os.system('echo 1 > /proc/sys/kernel/sysrq')
    os.system('echo c > /proc/sysrq-trigger')


def reboot():
    """
    reboot - simulate node crash as close as possible
    https://man7.org/linux/man-pages/man1/systemctl.1.html
    """
    os.system('reboot -f -f')


def network_interface_down():
    """
    simulate network failure
    """
    print(f"network interface down: {time.time()}")
    os.system('sudo ip link set eth0 down')
    for t in range(200):
        time.sleep(0.1)
        print(f"network interface down: {time.time()}")
    os.system('sudo ip link set eth0 up')
    print(f"network interface up: {time.time()}")
    return True


def simulate_power_failure():
    """
    simulate power failure
    """
    print(f"simulate power failure: {time.time()}")
    network_interface_down()
    reboot()
    return True


# def start_session():
#     session_name = "my_session"
#     server = tmux.Server()
#     session = server.new_session(session_name=session_name, attach=False, window_name="main")
#     server.cmd("set", "-g", "pane-border-status", "top")
#     return server, session
#
#
# def run_in_tmux(session, function_name):
#     # get function using function name
#     function = globals()[function_name]
#
#     # create window
#     window = session.new_window(attach=False)
#     # create pane
#     pane = window.panes[0]
#     # run function in pane
#     pane.send_keys(function)
#
#
# def terminate_tmux(server):
#     server.kill_server()


if __name__ == '__main__':
    # read command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    # add argument for function name with -f or --function_name
    parser.add_argument('-f', '--function_name', type=str, required=True)
    args = parser.parse_args()

    # call function
    print(f"calling function: {args.function_name}")
    function_name = args.function_name
    function = globals()[function_name]
    function()


