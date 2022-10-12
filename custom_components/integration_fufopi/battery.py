from ast import Str
from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_POWER,
    POWER_WATT,
    DEVICE_CLASS_BATTERY,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_BATTERY_CHARGING,
)

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, ATTRIBUTION


class BatteryCoordinator:
    """Coordinator class for battery"""

    def __init__(self) -> None:
        self._voltage = Decimal(0)
        self._current = Decimal(0)

    @property
    def voltage(self):
        """return battery voltage in V"""
        return self._voltage.quantize(Decimal("1.000"))

    @voltage.setter
    def voltage(self, new_value):
        if isinstance(new_value, str):
            ## value in mv
            self._voltage = Decimal(new_value)
        elif isinstance(new_value, Decimal):
            self._voltage = new_value
        else:
            raise ValueError

    @property
    def current(self):
        """return battery current in A"""
        return self._current.quantize(Decimal("1.000"))

    @current.setter
    def current(self, new_value):
        if isinstance(new_value, str):
            ## value in mA
            self._current = Decimal(new_value) * Decimal(0.001)
        elif isinstance(new_value, Decimal):
            self._current = new_value
        else:
            raise ValueError

    @property
    def power(self):
        """return battery power in W"""
        return (self._voltage * self._current).quantize(Decimal("1.000"))

    @property
    def is_charging(self):
        """return True if battery is charging"""
        return self._current > Decimal(0)

    @property
    def per_cent(self):
        """return the amount of battery in per cent"""
        _data = [
            (Decimal(9.0), Decimal(0.0)),
            (Decimal(10.0), Decimal(20.0)),
            (Decimal(11.0), Decimal(40.0)),
            (Decimal(12.0), Decimal(60.0)),
            (Decimal(13.0), Decimal(80.0)),
            (Decimal(14.0), Decimal(100.0)),
            (Decimal(15.0), Decimal(120.0)),
        ]
        _min_voltage, _min_per_cent = _data[0]
        if self._voltage >= _min_voltage:
            for _v, _per_cent in _data:
                if self._voltage == _v:
                    return _per_cent.quantize(Decimal("1.0"))

                if self._voltage < _v:
                    return self._scale(
                        self._voltage, (_v, _per_cent), (_min_voltage, _min_per_cent)
                    ).quantize(Decimal("1.0"))
                else:
                    _min_voltage = _v
                    _min_per_cent = _per_cent

        return Decimal(0)

    def _scale(self, x, upper, lower):
        _x1, _y1 = lower
        _x2, _y2 = upper
        _m = (_y2 - _y1) / (_x2 - _x1)
        _n = _m * _x1 - _y1
        return x * _m - _n


class BatteryEntity(CoordinatorEntity):
    """VE Direct base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._batt = BatteryCoordinator
        self._batt = self.coordinator.batt

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "batt"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "batt_model")},
            "name": "Battery",
            "model": "batt_model",
            "manufacturer": "Eleksol",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class BatteryVoltageSensor(BatteryEntity, SensorEntity):
    """Battery voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    @property
    def unique_id(self):
        return super().unique_id + "V"

    @property
    def name(self):
        return "Battery voltage"

    @property
    def native_value(self):
        return self._batt.voltage


class BatteryCurrentSensor(BatteryEntity, SensorEntity):
    """Battery voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def name(self):
        return "Battery current"

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @property
    def native_value(self):
        return self._batt.current


class PowerToBattSensor(BatteryEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Battery in power"

    @property
    def unique_id(self):
        return super().unique_id + "PTB"

    @property
    def native_value(self):
        if self._batt.is_charging:
            return self._batt.power

        return Decimal(0)


class PowerFromBattSensor(BatteryEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Battery out power"

    @property
    def unique_id(self):
        return super().unique_id + "PFB"

    @property
    def native_value(self):
        if not self._batt.is_charging:
            return self._batt.power * Decimal(-1)

        return Decimal(0)


class BatteryStateBinarySensor(BatteryEntity, BinarySensorEntity):
    """battery state binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_BATTERY_CHARGING

    @property
    def unique_id(self):
        return super().unique_id + "BS"

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return "Battery is charging"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._batt.is_charging


class BatteryPerCentSensor(BatteryEntity, SensorEntity):
    """% of battery capacity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_BATTERY
        self._attr_native_unit_of_measurement = "%"

    @property
    def unique_id(self):
        return super().unique_id + "BPC"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Battery left"

    @property
    def native_value(self):
        return self._batt.per_cent
