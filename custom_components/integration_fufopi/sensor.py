"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from unicodedata import decimal
from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
)

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity, ClimaDHTEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _sensors = []
    for key in list(coordinator.data.keys()):
        _sensors.append(IntegrationBlueprintSensor(coordinator, entry, key))

    _sensors.append(PowerFromBattSensor(coordinator, entry))
    _sensors.append(PowerToBattSensor(coordinator, entry))
    _sensors.append(LoadPowerSensor(coordinator, entry))
    _sensors.append(BatteryPerCentSensor(coordinator, entry))

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


class BatteryPerCentSensor(VEDirectEntity, SensorEntity):
    """% of battery capacity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "BPC")
        self._attr_device_class = DEVICE_CLASS_BATTERY

        self.scale = [
            (9000, 0.0),
            (10000, 20.0),
            (11000, 40.0),
            (12000, 60.0),
            (13000, 80.0),
            (14000, 100.0),
            (15000, 120.0),
        ]

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Battery left"

    @property
    def native_value(self):
        _v_batt = self.coordinator.data["V"]["value"]
        if _v_batt >= Decimal(9000):
            for _i in range(len(self.scale)):
                _v, _percent = self.scale[_i]
                if _v_batt == Decimal(_v):
                    return Decimal(_percent)

                if _v_batt < Decimal(_v):
                    _v_last, _percent_last = self.scale[_i - 1]
                    _m = (_percent - _percent_last) / (_v - _v_last)
                    _n = _m * _v_last - _percent_last

                    return Decimal((_v_batt * Decimal(_m)) - Decimal(_n)).quantize(
                        Decimal("1.0")
                    )

        return Decimal(0)


class ClimaTemperatureSensor(ClimaDHTEntity, SensorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Temperatura"

    @property
    def native_value(self):
        return self.coordinator.clima_data["temp_c"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "temp"


class ClimaHumiditySensor(ClimaDHTEntity, SensorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_HUMIDITY

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Humidity"

    @property
    def native_value(self):
        return self.coordinator.clima_data["humidity"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "hum"
