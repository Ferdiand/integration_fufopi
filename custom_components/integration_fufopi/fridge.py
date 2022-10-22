from ast import Str
from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_POWER,
    POWER_WATT,
)

from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, ATTRIBUTION


class FridgeEntity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.relay_index = 1

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "fridge"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "Drehia")},
            "name": "Drehia CBX-55",
            "model": "CBX-55",
            "manufacturer": "Drehia",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class FridgePowerSwitch(FridgeEntity, SwitchEntity):
    """integration_blueprint switch class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Fridge Power"
        self._attr_device_class = DEVICE_CLASS_OUTLET

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return super().unique_id + "power"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_on()
        # self._attr_is_on = True
        # self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_off()
        # self._attr_is_on = False
        # self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.relay_board.relay[self.relay_index].is_on


class FridgeCurrentSensor(FridgeEntity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Fridge current"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.smart_solar.panel_voltage) * Decimal(0.001)
        _i = Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)
        _i = _i - Decimal(0.5)
        if self.coordinator.relay_board.relay[self.relay_index].is_on:
            self._attr_native_value = _i.quantize(Decimal("1.000"))
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()


class FridgePowerSensor(FridgeEntity, SensorEntity):
    """Solar panel power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Fridge power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "P"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.smart_solar.panel_voltage) * Decimal(0.001)
        _i = Decimal(self.coordinator.smart_solar.load_current) * Decimal(0.001)
        _i = _i - Decimal(0.5)
        if self.coordinator.relay_board.relay[self.relay_index].is_on:
            self._attr_native_value = (_i * _v).quantize(Decimal("1.000"))
        else:
            self._attr_native_value = Decimal(0)
        self.async_write_ha_state()
