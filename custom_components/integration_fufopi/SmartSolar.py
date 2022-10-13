from msilib.schema import Property


class SmartSolarCoordinator:
    """Victron Smart Solar charger coordinator"""

    def __init__(self) -> None:
        self._data = {}

    @property
    def product_id(self):
        """return product ID"""
        return self._data["PID"]

    @property
    def firmware(self):
        """return firmware version"""
        return self._data["FW"]

    @property
    def serial_number(self):
        """return serial number"""
        return self._data["SER#"]

    @property
    def state_of_operation(self):
        """return state of operation"""
        return self._data["CS"]

    @property
    def tracker_operation_mode(self):
        """return tracker operation mode"""
        return self._data["MPPT"]

    @property
    def off_reason(self):
        """return off reason"""
        return self._data["OR"]

    @property
    def day_seq_number(self):
        """return day sequence number"""
        return self._data["HSDS"]

    @property
    def checksum(self):
        """return checksum"""
        return self._data["Checksum"]

    @property
    def load_current(self):
        """return load current in mA"""
        return self._data["IL"]

    @property
    def error_reason(self):
        """return the error reason"""
        return self._data["ERR"]

    @property
    def load_state(self):
        """return the load state"""
        return self._data["LOAD"]
