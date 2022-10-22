from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_POWER,
    POWER_WATT,
)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN, ATTRIBUTION


class PowerDistributionEntity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "pwdist"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "powerdist_model")},
            "name": "Power distribution",
            "model": "pwdist_model",
            "manufacturer": "Ermenda",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class LoadCurrentSensor(PowerDistributionEntity, SensorEntity):
    """Load current sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Load current"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def unique_id(self):
        return super().unique_id + "LI"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = (
            Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)
        ).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class LoadPowerSensor(PowerDistributionEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Load power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "LP"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.smart_solar.battery_voltage) * Decimal(0.001)
        _i = Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)

        self._attr_native_value = (_v * _i).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class LoadStateBinarySensor(PowerDistributionEntity, BinarySensorEntity):
    """load state binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Load state"
        self._attr_device_class = DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        return super().unique_id + "LS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.smart_solar.load_state == "ON":
            self._attr_is_on = True
        else:
            self._attr_is_on = False

        self.async_write_ha_state()


class RpiCurrentSensor(PowerDistributionEntity, SensorEntity):
    """Rpi current sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Rpi current"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def unique_id(self):
        return super().unique_id + "RpiI"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.relay_board.relay[1].is_on:
            self._attr_native_value = (Decimal(0.5)).quantize(Decimal("1.000"))
        else:
            self._attr_native_value = (
                Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)
            ).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class RpiPowerSensor(PowerDistributionEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Rpi power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "RpiP"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.smart_solar.battery_voltage) * Decimal(0.001)
        _i = Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)

        self._attr_native_value = (_v * _i).quantize(Decimal("1.000"))

        self.async_write_ha_state()
