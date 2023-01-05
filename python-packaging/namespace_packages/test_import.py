try:
    import riaps.interfaces.modbus.modbus as modbus
    print("modbus installed")
except ImportError as e:
    print(e)

try:
    import riaps.interfaces.canbus.canbus as canbus
    print("canbus installed")
except ImportError as e:
    print(e)

try:
    import riaps.interfaces.mqtt.mqtt as mqtt
    print("mqtt installed")
except ImportError as e:
    print(e)

