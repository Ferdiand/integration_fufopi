from ast import Str
from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
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
from .SmartSolar import SmartSolarCoordinator


class BatteryEntity(CoordinatorEntity):
    """VE Direct base entity"""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry

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
        self._attr_name = "Battery voltage"
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    @property
    def unique_id(self):
        return super().unique_id + "V"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.battery_voltage) * Decimal(
            0.001
        ).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class BatteryCurrentSensor(BatteryEntity, SensorEntity):
    """Battery voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Battery current"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = (
            Decimal(self.coordinator.battery_current) * Decimal(0.001)
        ).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class PowerToBattSensor(BatteryEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Battery in power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "PTB"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.battery_voltage)
        _i = Decimal(self.coordinator.battery_current)

        if _i > Decimal(0):
            self._attr_native_value = (_v * _i * Decimal(0.001)).quantize(
                Decimal("1.000")
            )
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()


class PowerFromBattSensor(BatteryEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Battery out power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "PFB"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.battery_voltage) * Decimal(0.001)
        _i = Decimal(self.coordinator.battery_current) * Decimal(0.001)

        if _i < Decimal(0):
            self._attr_native_value = (_v * _i * Decimal(-1.0)).quantize(
                Decimal("1.000")
            )
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()


class BatteryStateBinarySensor(BatteryEntity, BinarySensorEntity):
    """battery state binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Battery is charging"
        self._attr_device_class = DEVICE_CLASS_BATTERY_CHARGING

    @property
    def unique_id(self):
        return super().unique_id + "BS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _i = Decimal(self.coordinator.battery_current)

        if _i > Decimal(0):
            self._attr_is_on = True
        else:
            self._attr_is_on = False

        self.async_write_ha_state()


class BatteryPerCentSensor(BatteryEntity, SensorEntity):
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
            (Decimal(9.0), Decimal(0.0)),
            (Decimal(10.0), Decimal(20.0)),
            (Decimal(11.0), Decimal(40.0)),
            (Decimal(12.0), Decimal(60.0)),
            (Decimal(13.0), Decimal(80.0)),
            (Decimal(14.0), Decimal(100.0)),
            (Decimal(15.0), Decimal(120.0)),
        ]

        _min_voltage, _min_per_cent = _data[0]
        _voltage = Decimal(self.coordinator.battery_voltage) * Decimal(0.001)

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
