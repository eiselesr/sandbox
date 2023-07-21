# riaps:keep_import:begin
import inspect

from app.DemoDevice import DemoDevice

from test_suite.testInterface import TestInterface
# riaps:keep_import:end


class DemoDevice_test(DemoDevice):

    # riaps:keep_constr:begin
    def __init__(self):
        super().__init__()

        self.function_patches = {
            "faulty_on_tick": faulty_on_tick
        }

        TestInterface(self, self.logger)
    # riaps:keep_constr:end


# riaps:keep_impl:begin
def faulty_on_tick(self):
    now = self.tick.recv_pyobj()
    self.logger.info(f"TestInterface | faulty_on_tick | now: {now}")
# riaps:keep_impl:end
