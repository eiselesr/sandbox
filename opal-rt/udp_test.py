import sys
import socket
import scapy
import select
import struct


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')


    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.settimeout(1)
    s1.bind(("224.0.0.1", 23002))

    timeout = 100
    ready_sockets, _, _ = select.select(
        [s1], [], [], timeout)


    while ready_sockets:
        try:
            data, addr = s1.recvfrom(32)
            header = struct.unpack('<Q', data[0:8])

            if header[0] == 18911916:
                print("valid header")

                try:
                    value = struct.unpack('<QQQQ', data)  # little-endian
                except struct.error as e:
                    print(e)
                    continue

                connected = value[1]

                if connected != 0 and connected != 1:
                    print(f"invalid breaker status")
                    continue

                sender_id = value[2]
                # sender_id = 123

                if sender_id not in [131]:
                    print(f"invalid breaker id: {sender_id}")
                    continue


                timestamp = value[3]
                ip = addr[0]
                port = addr[1]
                print(f"relay: {sender_id} status: {connected} from {ip}:{port} time:{timestamp}")
                ready_sockets, _, _ = select.select(
                    [s1], [], [], timeout)

        except socket.timeout:
            print("No data on s1")

    print(f"No data in {timeout} seconds. Close listener.")



    #
    # while True:
    #     try:
    #         data1, addr1 = s1.recvfrom(8)
    #         value1 = struct.unpack('<d', data1)  # little-endian
    #         print(f"value1: {value1} from: {addr1}")
    #     except socket.timeout:
    #         print("No data on s1")



