from .base import ZIBaseInstrument
from qcodes.instrument.channel import InstrumentChannel
import qcodes.utils.validators as vals

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.mfli import DAQModule, SweeperModule


class DAQ(InstrumentChannel):
    """
    test docstring here
    
    """

    def __init__(self, name, parent_instr, parent_contr):
        super().__init__(parent_instr, name)
        self._daq_module = DAQModule(parent_contr)
        self._daq_module._setup()
        for k, param in self._daq_module.__dict__.items():
            if not k.startswith("_"):
                val_mapping = None
                if param._map:
                    val_mapping = dict(map(reversed, param._map.items()))
                    param._map = None
                self.add_parameter(
                    k,
                    get_cmd=param,
                    set_cmd=param,
                    docstring=param._description,
                    unit=param._unit,
                    val_mapping=val_mapping,
                )

    def trigger(self, *args):
        self._daq_module.trigger(*args)

    def signals_add(self, *args, **kwargs):
        return self._daq_module.signals_add(*args, **kwargs)

    def signals_clear(self):
        self._daq_module.signals_clear()

    def measure(self, **kwargs):
        self._daq_module.measure(**kwargs)

    def _set(self, *args):
        self._daq_module._set(*args)

    def _get(self, *args, valueonly=True):
        return self._daq_module._get(*args)

    @property
    def signals(self):
        return self._daq_module.signals

    @property
    def results(self):
        return self._daq_module.results


class Sweeper(InstrumentChannel):
    """
    sweeper docstring here
    
    """

    def __init__(self, name, parent_instr, parent_contr):
        super().__init__(parent_instr, name)
        self._sweeper_module = SweeperModule(parent_contr)
        self._sweeper_module._setup()
        for k, param in self._sweeper_module.__dict__.items():
            if not k.startswith("_"):
                val_mapping = None
                if param._map:
                    val_mapping = dict(map(reversed, param._map.items()))
                    param._map = None
                self.add_parameter(
                    k,
                    get_cmd=param,
                    set_cmd=param,
                    docstring=param._description,
                    unit=param._unit,
                    val_mapping=val_mapping,
                )

    def signals_add(self, signal_source):
        return self._sweeper_module.signals_add(signal_source)

    def signals_clear(self):
        self._sweeper_module.signals_clear()

    def signals_list(self):
        return self._sweeper_module.signals_list()

    def sweep_parameter(self, param):
        self._sweeper_module.sweep_parameter(param)

    def measure(self, **kwargs):
        self._sweeper_module.measure(**kwargs)

    def application(self, application):
        self._sweeper_module.application(application)

    def _set(self, *args):
        self._sweeper_module._set(*args)

    def _get(self, *args, valueonly=True):
        return self._sweeper_module._get(*args)

    @property
    def signals(self):
        return self._sweeper_module.signals

    @property
    def results(self):
        return self._sweeper_module.results


class MFLI(ZIBaseInstrument):
    """
    QCoDeS driver for ZI MFLI.

    Inherits from ZIBaseInstrument.
    """

    def __init__(
        self,
        name: str,
        serial: str,
        interface="1gbe",
        host="localhost",
        port=8004,
        api=6,
        **kwargs
    ) -> None:
        super().__init__(name, "mfli", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        blacklist = ["scopes"]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def connect(self):
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.MFLI(
            self._name, self._serial, interface=self._interface, host=self._host
        )
        self._controller.setup()
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()
        self.add_submodule("daq", DAQ("daq", self, self._controller))
        self.add_submodule("sweeper", Sweeper("sweeper", self, self._controller))

    def get_idn(self):
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller._get("system/fwrevision"),
        )
