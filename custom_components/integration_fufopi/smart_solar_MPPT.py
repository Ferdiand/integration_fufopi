""" Smart Solar MPPT"""
from decimal import Decimal
from homeassistant.core import callback

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.components.sensor import SensorEntity

from homeassistant.const import (
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_BATTERY,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    POWER_WATT,
)

from .const import DOMAIN, ATTRIBUTION

PID_VALUE_LIST = {"0xA060": "SmartSolar MPPT 100|20 48V"}

CS_VALUE_LIST = {
    "0": "Off",
    "2": "Fault",
    "3": "Bulk",
    "4": "Absorption",
    "5": "Float",
    "6": "Storage",
    "7": "Equalize (manual)",
    "9": "Inverting",
    "11": "Power supply",
    "245": "Starting-up",
    "246": "Repeated absorption",
    "247": "Auto equalize / Recondition",
    "248": "BatterySafe",
    "252": "External Control",
}

MPPT_VALUE_LIST = {
    "0": "Off",
    "1": "Voltage or current limited",
    "2": "MPP Tracker active",
}

OR_VALUE_LIST = {
    "0x00000000": "No reason",
    "0x00000001": "No input power",
    "0x00000002": "Switched off (power switch)",
    "0x00000004": "Switched off (device mode register) ",
    "0x00000008": "Remote input",
    "0x00000010": "Protection active ",
    "0x00000020": "Paygo",
    "0x00000040": "BMS",
    "0x00000080": "Engine shutdown",
    "0x00000100": "Analysing input voltage",
}

ERR_VALUE_LIST = {
    "0": "No error",
    "2": "Battery voltage too high",
    "17": "Charger temperature too high",
    "18": "Charger over current",
    "19": "Charger current reversed",
    "20": "Bulk time limit exceeded",
    "21": "Current sensor issue (sensor bias/sensor broken)",
    "26": "Terminals overheated",
    "28": "Converter issue (dual converter models only)",
    "33": "Input voltage too high (solar panel)",
    "34": "Input current too high (solar panel)",
    "38": "Input shutdown (due to excessive battery voltage)",
    "39": "Input shutdown (due to current flow during off mode)",
    "65": "Lost communication with one of devices",
    "66": "Synchronised charging device configuration issue",
    "67": "BMS connection lost",
    "68": "Network misconfigured",
    "116": "Factory calibration data lost",
    "117": "Invalid/incompatible firmware",
    "119": "User settings invalid",
}


def add_smart_solar_mppt_sensors(sensors, coordinator, config_entry):
    """append sensors"""
    sensors.append(SmartSolarProductIDSensor(coordinator, config_entry))
    sensors.append(SmartSolarFirmwareSensor(coordinator, config_entry))
    sensors.append(SmartSolarSerialNumberSensor(coordinator, config_entry))
    sensors.append(SmartSolarCSSensor(coordinator, config_entry))
    sensors.append(SmartSolarMPPTSensor(coordinator, config_entry))
    sensors.append(SmartSolarHSDSSensor(coordinator, config_entry))
    sensors.append(SmartSolarCSSensor(coordinator, config_entry))
    sensors.append(SmartSolarCSSensor(coordinator, config_entry))
    sensors.append(SmartSolarILSensor(coordinator, config_entry))
    sensors.append(SmartSolarISensor(coordinator, config_entry))
    sensors.append(SmartSolarVSensor(coordinator, config_entry))
    sensors.append(SmartSolarVPVSensor(coordinator, config_entry))
    sensors.append(SmartSolarPPVSensor(coordinator, config_entry))
    sensors.append(SmartSolarH19Sensor(coordinator, config_entry))
    sensors.append(SmartSolarH20Sensor(coordinator, config_entry))
    sensors.append(SmartSolarH21Sensor(coordinator, config_entry))
    sensors.append(SmartSolarH22Sensor(coordinator, config_entry))
    sensors.append(SmartSolarH23Sensor(coordinator, config_entry))
    sensors.append(BatteryPerCentSensor(coordinator, config_entry))


class SmartSolarEntity(CoordinatorEntity):
    """Smart solar mppt base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "SmartSolar"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id + "SmartSolar")},
            "name": "SmartSolar MPPT 100|20 48V",
            "model": "HQ2129WD7QV",
            "manufacturer": "Victron Energy",
        }


class SmartSolarDiagnosticEntity(SmartSolarEntity):
    """Smart solar diagnostic entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_entity_category = "diagnostic"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "SmartSolar"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id + "SmartSolar")},
            "name": "SmartSolar MPPT 100|20 48V",
            "model": "HQ2129WD7QV",
            "manufacturer": "Victron Energy",
        }


class SmartSolarProductIDSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar Product ID Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Product ID"
        self._attr_icon = "mdi:identifier"

    @property
    def unique_id(self):
        return super().unique_id + "PID"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.product_id

        self.async_write_ha_state()


class SmartSolarFirmwareSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar Firmware Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Firmware Version"
        self._attr_icon = "mdi:identifier"

    @property
    def unique_id(self):
        return super().unique_id + "FW"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.firmware

        self.async_write_ha_state()


class SmartSolarSerialNumberSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar serial number Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Serial Number"
        self._attr_icon = "mdi:music-accidental-sharp"

    @property
    def unique_id(self):
        return super().unique_id + "SER#"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.serial_number

        self.async_write_ha_state()


class SmartSolarCSSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar operation state Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "State of operation"
        self._attr_icon = "mdi:car-turbocharger"

    @property
    def unique_id(self):
        return super().unique_id + "CS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.state_of_operation

        self.async_write_ha_state()


class SmartSolarMPPTSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar tracker op mode Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Tracker operation mode"
        self._attr_icon = "mdi:radar"

    @property
    def unique_id(self):
        return super().unique_id + "MPPT"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.tracker_operation_mode

        self.async_write_ha_state()


class SmartSolarORSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar off reason Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Off Reason"
        self._attr_icon = "mdi:playlist-remove"

    @property
    def unique_id(self):
        return super().unique_id + "OR"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.off_reason

        self.async_write_ha_state()


class SmartSolarHSDSSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar day seq number Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Day seq number"

    @property
    def unique_id(self):
        return super().unique_id + "HSDS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.day_seq_number

        self.async_write_ha_state()


class SmartSolarCheckSumSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar checksum Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Checksum"

    @property
    def unique_id(self):
        return super().unique_id + "Checksum"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.checksum

        self.async_write_ha_state()


class SmartSolarErrSensor(SmartSolarDiagnosticEntity, SensorEntity):
    """Smart solar checksum Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Error reason"

    @property
    def unique_id(self):
        return super().unique_id + "ERR"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.error_reason

        self.async_write_ha_state()


class SmartSolarILSensor(SmartSolarEntity, SensorEntity):
    """Smart solar checksum Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "IL"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_MILLIAMPERE

    @property
    def unique_id(self):
        return super().unique_id + "IL"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.load_current

        self.async_write_ha_state()


class SmartSolarISensor(SmartSolarEntity, SensorEntity):
    """Smart solar checksum Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "I"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_MILLIAMPERE

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.battery_current

        self.async_write_ha_state()


class SmartSolarVSensor(SmartSolarEntity, SensorEntity):
    """Smart solar checksum Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "V"
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT

    @property
    def unique_id(self):
        return super().unique_id + "V"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.battery_voltage

        self.async_write_ha_state()


class SmartSolarVPVSensor(SmartSolarEntity, SensorEntity):
    """Smart solar VPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "VPV"
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT

    @property
    def unique_id(self):
        return super().unique_id + "VPV"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.panel_voltage

        self.async_write_ha_state()


class SmartSolarPPVSensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "PPV"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "PPV"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.panel_power

        self.async_write_ha_state()


class SmartSolarH19Sensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "H19"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = "0,01 kWh"

    @property
    def unique_id(self):
        return super().unique_id + "H19"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.yield_total

        self.async_write_ha_state()


class SmartSolarH20Sensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "H20"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = "0,01 kWh"

    @property
    def unique_id(self):
        return super().unique_id + "H20"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.yield_today

        self.async_write_ha_state()


class SmartSolarH21Sensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "H21"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "H21"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.max_power_today

        self.async_write_ha_state()


class SmartSolarH22Sensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "H22"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = "0,01 kWh"

    @property
    def unique_id(self):
        return super().unique_id + "H22"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.yield_yesterday

        self.async_write_ha_state()


class SmartSolarH23Sensor(SmartSolarEntity, SensorEntity):
    """Smart solar PPV Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "H23"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "H23"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.smart_solar.max_power_yesterday

        self.async_write_ha_state()


class BatteryPerCentSensor(SmartSolarEntity, SensorEntity):
    """% of battery capacity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Battery left"
        self._attr_device_class = DEVICE_CLASS_BATTERY
        self._attr_native_unit_of_measurement = "%"

    @property
    def unique_id(self):
        return super().unique_id + "BPC"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _data = [
            (Decimal(9000), Decimal(0.0)),
            (Decimal(10000), Decimal(20.0)),
            (Decimal(11000), Decimal(40.0)),
            (Decimal(12000), Decimal(60.0)),
            (Decimal(13000), Decimal(80.0)),
            (Decimal(14000), Decimal(100.0)),
            (Decimal(15000), Decimal(120.0)),
        ]

        _min_voltage, _min_per_cent = _data[0]
        _voltage = Decimal(self.coordinator.smart_solar.battery_voltage) * Decimal(
            0.001
        )

        self._attr_native_value = Decimal(0)

        if _voltage >= _min_voltage:
            for _v, _per_cent in _data:
                if _voltage == _v:
                    self._attr_native_value = _per_cent.quantize(Decimal("1.0"))

                elif _voltage < _v:
                    self._attr_native_value = self._scale(
                        _voltage, (_v, _per_cent), (_min_voltage, _min_per_cent)
                    ).quantize(Decimal("1.0"))
                else:
                    _min_voltage = _v
                    _min_per_cent = _per_cent

        self.async_write_ha_state()

    def _scale(self, x, upper, lower):
        _x1, _y1 = lower
        _x2, _y2 = upper
        _m = (_y2 - _y1) / (_x2 - _x1)
        _n = _m * _x1 - _y1
        return x * _m - _n
