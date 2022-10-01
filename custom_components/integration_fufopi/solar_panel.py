from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_ENERGY,
    POWER_WATT,
    ENERGY_KILO_WATT_HOUR,
)

from homeassistant.components.sensor import SensorEntity, STATE_CLASS_TOTAL_INCREASING

from .const import DOMAIN, ATTRIBUTION


class SolarPanelCoordinator:
    """Coordinator class for battery"""

    def __init__(self) -> None:
        self._voltage = Decimal(0)
        self._power = Decimal(0)
        self._yield_today = Decimal(0)
        self._max_power_today = Decimal(0)

    @property
    def voltage(self):
        """return battery voltage in V"""
        return self._voltage.quantize(Decimal("1.000"))

    @voltage.setter
    def voltage(self, new_value):
        if isinstance(new_value, str):
            ## value in mv
            self._voltage = Decimal(new_value) * Decimal(0.001)
        elif isinstance(new_value, Decimal):
            self._voltage = new_value
        else:
            raise ValueError

    @property
    def current(self):
        """return solar panel current in A"""
        if self._voltage > Decimal(0):
            return (self._power / self._voltage).quantize(Decimal("1.000"))

        return Decimal(0)

    @property
    def power(self):
        """return battery power in W"""
        return self._power.quantize(Decimal("1.000"))

    @power.setter
    def power(self, new_value):
        if isinstance(new_value, str):
            ## value in W
            self._power = Decimal(new_value)
        elif isinstance(new_value, Decimal):
            self._power = new_value
        else:
            raise ValueError

    @property
    def yield_today(self):
        """return the yield today in kWh"""
        return self._yield_today.quantize(Decimal("1.000"))

    @yield_today.setter
    def yield_today(self, new_value):
        if isinstance(new_value, str):
            ## value in 0.01 kWh
            self._power = Decimal(new_value) * Decimal(0.01)
        elif isinstance(new_value, Decimal):
            self._power = new_value
        else:
            raise ValueError

    @property
    def max_power_today(self):
        """return max power today in W"""
        return self._max_power_today.quantize(Decimal("1.000"))

    @max_power_today.setter
    def max_power_today(self, new_value):
        if isinstance(new_value, str):
            ## value in W
            self._max_power_today = Decimal(new_value)
        elif isinstance(new_value, Decimal):
            self._max_power_today = new_value
        else:
            raise ValueError


class SolarPanelEntity(CoordinatorEntity):
    """Solar panel base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._solar_panel = SolarPanelCoordinator
        self._solar_panel = self.coordinator.solar_panel

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "solar_panel"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "solar_panel_model")},
            "name": "Solar panel",
            "model": "solar_panel_model",
            "manufacturer": "Chinito",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class SolarPanelVoltageSensor(SolarPanelEntity, SensorEntity):
    """Solar panel voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    @property
    def unique_id(self):
        return super().unique_id + "V"

    @property
    def name(self):
        return "Solar panel voltage"

    @property
    def native_value(self):
        return self._solar_panel.voltage


class SolarPanelCurrentSensor(SolarPanelEntity, SensorEntity):
    """SolarPanel voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def name(self):
        return "Solar panel current"

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @property
    def native_value(self):
        return self._solar_panel.current


class SolarPanelPowerSensor(SolarPanelEntity, SensorEntity):
    """Solar panel power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Solar panel power"

    @property
    def unique_id(self):
        return super().unique_id + "P"

    @property
    def native_value(self):
        return self._solar_panel.power


class SolarPanelYieldTodaySensor(SolarPanelEntity, SensorEntity):
    """Yield today power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Solar panel yield today"

    @property
    def unique_id(self):
        return super().unique_id + "YT"

    @property
    def native_value(self):
        return self._solar_panel.yield_today
