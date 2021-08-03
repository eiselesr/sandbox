import sys
import socket
import scapy
import struct


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')

    # value = struct.unpack('<d', b'\xeb\x47\x4c\x28\xb4\xbb\x99\x3f')[0]  # little-endian
    # print(value)

    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.settimeout(1)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2.settimeout(1)

    # s1.bind(("10.1.4.244", 23002))
    s1.bind(("224.0.0.1", 23002))
    # s2.bind(("10.1.4.244", 25000))
    # s2.bind(("224.0.0.1", 25000))

    while True:
        try:
            data1, addr1 = s1.recvfrom(8)
            value1 = struct.unpack('<d', data1)  # little-endian
            print(f"value1: {value1} from: {addr1}")
        except socket.timeout:
            print("No data on s1")
        # try:
        #     data2, addr2 = s2.recvfrom(16)
        #     value2 = struct.unpack('<xxxxxxxxd', data2)  # little-endian
        #     print(f"value2: {value2} from: {addr2}")
        except socket.timeout:
            print("No data on s2")

        # print(f"data1: {data1}")
        # print(f"data2: {data2}")



