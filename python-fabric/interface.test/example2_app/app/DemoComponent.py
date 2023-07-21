# riaps:keep_import:begin
from riaps.run.comp import Component
# riaps:keep_import:end


class DemoComponent(Component):

    # riaps:keep_constr:begin
    def __init__(self):
        super().__init__()
    # riaps:keep_constr:end

    # riaps:keep_tick:begin
    def on_tick(self):
        now = self.tick.recv_pyobj()
        self.logger.info(f"DemoComponent | on_tick | now: {now}")
    # riaps:keep_tick:end

    # riaps:keep_impl:begin
    # riaps:keep_impl:end
