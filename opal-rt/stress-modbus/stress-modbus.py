import argparse
from modbus_tk import modbus_tcp
import modbus_tk.defines as cst
import yaml

from libs.Logger import EventLogger, unpack_bytes, pack_bytes

class ModbusDevice:
    def __init__(self, name, device_cfg, control_cfg):

        self.name = name
        self.EL = EventLogger(name)
        self.EL.info("STARTING")

        with open(control_cfg, 'r') as control_cfg:
            self.control_cfg = yaml.safe_load(control_cfg)

        with open(device_cfg, 'r') as device_cfg:
            self.device_cfg = yaml.safe_load(device_cfg)  # Load config file to interact with Modbus device

        self.mode = "GridConnect"
        # self.control = MicrogridControl.MicrogridControl(logger=self.logger,
        #                                                  dvc=self.dvc,
        #                                                  ctrl_cfg=self.control_cfg,
        #                                                  mode=self.mode)


        self.modbus_devices = list(self.device_cfg.keys())
        self.dvc = self.device_cfg[self.modbus_devices[0]]
        self.slave = self.dvc['Slave']
        addr = self.dvc['Address']
        port = self.dvc['Port']
        self.debugMode = self.dvc["debugMode"]

        if self.debugMode:
            print(f"addr: {addr}\n"
                  f"port: {port}")

        self.master = modbus_tcp.TcpMaster(addr, port)
        # self.master.set_timeout(ModbusSystem.Timeouts.TCPComm)
        # self.master.set_verbose(ModbusSystem.Debugging.Verbose)

    def explicit_test(self):

        response = self.master.execute(self.slave,
                                       getattr(cst, "READ_INPUT_REGISTERS"),
                                       27,
                                       quantity_of_x=1,
                                       output_value=[-1],
                                       data_format="")

        if self.debugMode:
            print(response)

    def test(self, dvc_name):

        device_name = dvc_name
        params = self.control_cfg[self.mode]["control_params"]
        # polling is based on mode of the microgrid
        msg = DeviceMessage()
        msg.device = device_name
        msg.operation = "READ"
        msg.param = params
        msg.value = [-1] * len(params)

        values = []

        tag = self.EL.new_trace(f"{self.name} query start")
        for idx, param in enumerate(msg.param):

            param_op = f"{param}_{msg.operation}"
            modbus_func = self.device_cfg[msg.device][param_op]
            # read Modbus command parameters from yaml file
            function_code = modbus_func['function']
            starting_address = modbus_func['start']
            length = modbus_func['length']
            value = msg.value[idx]

            modbus_value = [int(value / modbus_func['Units'][0])]
            data_fmt = modbus_func['data_format']

            if self.debugMode:
                print(f"function_code: {function_code}\n"
                      f"starting_address: {starting_address}\n"
                      f"quantity_of_x: {length}\n"
                      f"output_value: {modbus_value}\n"
                      f"data_format: {data_fmt}")

            tag = self.EL.tracepoint(tag, f"modbus query {param} start")
            response = self.master.execute(self.slave,
                                           getattr(cst, function_code),
                                           starting_address,
                                           quantity_of_x=length,
                                           output_value=modbus_value,
                                           data_format=data_fmt)
            tag = self.EL.tracepoint(tag, f"modbus query {param} stop")
            value = response[0] * modbus_func['Units'][0]
            values.append(value)

            if self.debugMode:
                print(response)

        if self.debugMode:
            print(f"params: {params}")
            print(f"values: {values}")

        tag = self.EL.tracepoint(tag, f"{self.name} query stop")



class DeviceMessage:
    device = ""
    operation = ""
    param = [""]  # of strings
    value = [0]  # of floats


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("n_loops")
    args = parser.parse_args()
    n_loops = int(args.n_loops)

    gen1_dvc = ModbusDevice(f"{args.name}_1", "cfg/gen1.yaml", "cfg/gen_control.yaml")
    gen2_dvc = ModbusDevice(f"{args.name}_2", "cfg/gen2.yaml", "cfg/gen_control.yaml")

    loop = 0
    while loop < n_loops:
        gen1_dvc.test(dvc_name="Gen1")
        loop += 1
        gen2_dvc.test(dvc_name="Gen2")
        loop += 1



    # if "relay" in args.name:
    #     dvc = ModbusDevice(args.name, "cfg/relay.yaml", "cfg/relay_control.yaml", n_loops)
    #     dvc.test(dvc_name="F1PCC")
    # elif "gen1" in args.name:
    #     gen1_dvc = ModbusDevice(args.name, "cfg/gen1.yaml", "cfg/gen_control.yaml", n_loops)
    #     gen1_dvc.test(dvc_name="Gen1")
    # elif "gen2" in args.name:
    #     gen2_dvc = ModbusDevice(args.name, "cfg/gen2.yaml", "cfg/gen_control.yaml", n_loops)
    #     gen2_dvc.test(dvc_name="Gen2")
    # else:
    #     print("What are you doing here?")
