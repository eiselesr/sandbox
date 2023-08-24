# riaps:keep_import:begin
import inspect

from app.DemoDevice import DemoDevice

from test_suite.testInterface import InjectionServer
# riaps:keep_import:end


class DemoDevice_test(DemoDevice):

    # riaps:keep_constr:begin
    def __init__(self):
        super().__init__()

    # riaps:keep_constr:end

    # Required for monkey patching
    def on_pytest_cmd_port(self):
        """
        This method is called when a message is received on the pytest_cmd_port from the InjectionServer thread.
        """
        msg = self.pytest_cmd_port.recv_pyobj()
        self.logger.info(f"DemoDevice | on_pytest_cmd_port | msg: {msg}")
        self.pub_pytest_cmd.send_pyobj(msg)

    def handleActivate(self):
        """
        This method is called when the component is activated.
        """
        self.logger.info(f"DemoDevice | handleActivate")
        super().handleActivate()

        # Required for monkey patching
        injection_server = InjectionServer(logger=self.logger, riaps_port=self.pytest_cmd_port)
        injection_server.start()



