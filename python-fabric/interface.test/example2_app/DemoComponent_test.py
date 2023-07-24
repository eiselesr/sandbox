# riaps:keep_import:begin
from app.DemoComponent import DemoComponent
from test_suite.testInterface import TestInterface
# riaps:keep_import:end


class DemoComponent_test(DemoComponent):

    # riaps:keep_constr:begin
    def __init__(self):
        super().__init__()

        self.function_patches = {
            "faulty_on_tick": faulty_on_tick
        }

        self.test_interface = TestInterface(self, self.logger)
    # riaps:keep_constr:end

    def on_sub_pytest_cmd(self):
        msg = self.sub_pytest_cmd.recv_pyobj()
        self.logger.info(f"DemoComponent | on_sub_pytest_cmd | msg: {msg}")

        self.test_interface.patch_function(msg["function"], msg["patch"])


# riaps:keep_impl:begin
def faulty_on_tick(self):
    now = self.tick.recv_pyobj()
    self.logger.info(f"DemoDevice | faulty_on_tick | now: {now}")
# riaps:keep_impl:end
