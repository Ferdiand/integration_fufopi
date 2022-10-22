from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

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


class SolarPanelEntity(CoordinatorEntity):
    """Solar panel base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

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
        self._attr_name = "Solar panel voltage"
        self._attr_device_class = DEVICE_CLASS_VOLTAGE
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    @property
    def unique_id(self):
        return super().unique_id + "V"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.smart_solar.panel_voltage
        ) * Decimal(0.001).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class SolarPanelCurrentSensor(SolarPanelEntity, SensorEntity):
    """SolarPanel voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel current"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def unique_id(self):
        return super().unique_id + "I"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _v = Decimal(self.coordinator.smart_solar.panel_voltage) * Decimal(0.001)
        _p = Decimal(self.coordinator.smart_solar.panel_power)
        if _v > Decimal(0):
            self._attr_native_value = (_p / _v).quantize(Decimal("1.000"))
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()


class SolarPanelPowerSensor(SolarPanelEntity, SensorEntity):
    """Solar panel power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel power"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "P"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.smart_solar.panel_power)
        self.async_write_ha_state()


class SolarPanelMaxPowerTodaySensor(SolarPanelEntity, SensorEntity):
    """Solar panel max power today sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel max power today"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "MPT"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.smart_solar.max_power_today)
        self.async_write_ha_state()


class SolarPanelMaxPowerYesterdaySensor(SolarPanelEntity, SensorEntity):
    """Solar panel max power yesterday sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel max power yesterday"
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def unique_id(self):
        return super().unique_id + "MPY"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.smart_solar.max_power_yesterday
        )
        self.async_write_ha_state()


class SolarPanelProductionTodaySensor(SolarPanelEntity, SensorEntity):
    """Solar panel production today power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel production today"
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def unique_id(self):
        return super().unique_id + "YT"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.smart_solar.yield_today
        ) * Decimal(0.01).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class SolarPanelProductionYesterdaySensor(SolarPanelEntity, SensorEntity):
    """Solar panel production today power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel production yesterday"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def unique_id(self):
        return super().unique_id + "YY"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.smart_solar.yield_yesterday
        ) * Decimal(0.01).quantize(Decimal("1.000"))
        self.async_write_ha_state()


class SolarPanelProductionTotalSensor(SolarPanelEntity, SensorEntity):
    """Solar panel production total power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Solar panel production total"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def unique_id(self):
        return super().unique_id + "YTT"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.smart_solar.yield_total
        ) * Decimal(0.01).quantize(Decimal("1.000"))
        self.async_write_ha_state()
