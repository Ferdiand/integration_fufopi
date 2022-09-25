"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from unicodedata import decimal
from homeassistant.components.sensor import SensorEntity, DEVICE_CLASS_POWER

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _sensors = []
    for key in list(coordinator.data.keys()):
        _sensors.append(IntegrationBlueprintSensor(coordinator, entry, key))

    _sensors.append(PowerFromBattSensor(coordinator, entry))
    _sensors.append(PowerToBattSensor(coordinator, entry))
    _sensors.append(LoadPowerSensor(coordinator, entry))

    async_add_devices(_sensors)


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        _data = self.coordinator.data[self.key]
        if "device_class" in list(_data.keys()):
            self._attr_device_class = _data["device_class"]
        if "unit_meassurement" in list(_data.keys()):
            self._attr_native_unit_of_measurement = _data["unit_meassurement"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.coordinator.data[self.key]["name"]

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        _data = self.coordinator.data[self.key]
        if isinstance(_data["value"], Decimal):
            _decimal = Decimal()
            _decimal = (_data["value"] * _data["unit_conversion"]).quantize(
                Decimal("1.000")
            )
            # _decimal = _decimal.quantize(Decimal("1.000"))
            self.coordinator.logger.warning(f"Decimal value {self.key} ::: {_decimal}")
            return _decimal

        if "value_list" in list(_data.keys()):
            return _data["value_list"][_data["value"]]

        return self.coordinator.data[self.key]["value"]

    @property
    def icon(self) -> str | None:
        _data = self.coordinator.data[self.key]
        if not isinstance(_data["value"], Decimal):
            if "icon" in list(_data.keys()):
                return _data["icon"]

        return super().icon


class PowerToBattSensor(VEDirectEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "PTB")
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = "W"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Power to Battery"

    @property
    def native_value(self):
        _v = (
            self.coordinator.data["V"]["value"]
            * self.coordinator.data["V"]["unit_conversion"]
        )
        _i = (
            self.coordinator.data["I"]["value"]
            * self.coordinator.data["I"]["unit_conversion"]
        )

        _zero = Decimal(0.0)

        if _i < _zero:
            return (_v * _i * Decimal(-1.0)).quantize(Decimal("1.000"))

        return Decimal(0.0)


class PowerFromBattSensor(VEDirectEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "PFB")
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = "W"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Power from Battery"

    @property
    def native_value(self):
        _v = (
            self.coordinator.data["V"]["value"]
            * self.coordinator.data["V"]["unit_conversion"]
        )
        _i = (
            self.coordinator.data["I"]["value"]
            * self.coordinator.data["I"]["unit_conversion"]
        )

        _zero = Decimal(0.0)

        if _i > _zero:
            return (_v * _i).quantize(Decimal("1.000"))

        return Decimal(0.0)


class LoadPowerSensor(VEDirectEntity, SensorEntity):
    """Calculated power sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "PL")
        self._attr_device_class = DEVICE_CLASS_POWER
        self._attr_native_unit_of_measurement = "W"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Load power"

    @property
    def native_value(self):
        _v = (
            self.coordinator.data["V"]["value"]
            * self.coordinator.data["V"]["unit_conversion"]
        )
        _i = (
            self.coordinator.data["IL"]["value"]
            * self.coordinator.data["IL"]["unit_conversion"]
        )

        return (_v * _i).quantize(Decimal("1.000"))
