"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from unicodedata import decimal
from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
)

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity, ClimaDHTEntity
from .battery import (
    BatteryVoltageSensor,
    BatteryCurrentSensor,
    PowerFromBattSensor,
    PowerToBattSensor,
    BatteryPerCentSensor,
)
from .solar_panel import (
    SolarPanelVoltageSensor,
    SolarPanelCurrentSensor,
    SolarPanelPowerSensor,
    SolarPanelProductionTodaySensor,
    SolarPanelMaxPowerTodaySensor,
    SolarPanelProductionYesterdaySensor,
    SolarPanelMaxPowerYesterdaySensor,
    SolarPanelProductionTotalSensor,
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _sensors = []
    for key in list(coordinator.data.keys()):
        _sensors.append(IntegrationBlueprintSensor(coordinator, entry, key))

    _sensors.append(BatteryCurrentSensor(coordinator, entry))
    _sensors.append(BatteryVoltageSensor(coordinator, entry))
    _sensors.append(PowerFromBattSensor(coordinator, entry))
    _sensors.append(PowerToBattSensor(coordinator, entry))
    _sensors.append(BatteryPerCentSensor(coordinator, entry))

    _sensors.append(SolarPanelPowerSensor(coordinator, entry))
    _sensors.append(SolarPanelVoltageSensor(coordinator, entry))
    _sensors.append(SolarPanelCurrentSensor(coordinator, entry))
    _sensors.append(SolarPanelProductionTodaySensor(coordinator, entry))
    _sensors.append(SolarPanelMaxPowerTodaySensor(coordinator, entry))
    _sensors.append(SolarPanelProductionYesterdaySensor(coordinator, entry))
    _sensors.append(SolarPanelMaxPowerYesterdaySensor(coordinator, entry))
    _sensors.append(SolarPanelProductionTotalSensor(coordinator, entry))

    _sensors.append(LoadPowerSensor(coordinator, entry))

    _sensors.append(ClimaTemperatureSensor(coordinator, entry))
    _sensors.append(ClimaHumiditySensor(coordinator, entry))

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
        _v = self.coordinator.batt.voltage
        _i = (
            self.coordinator.data["IL"]["value"]
            * self.coordinator.data["IL"]["unit_conversion"]
        )

        return (_v * _i).quantize(Decimal("1.000"))


class ClimaTemperatureSensor(ClimaDHTEntity, SensorEntity):
    """Tempreature sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

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
    """Humidity sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_HUMIDITY
        self._attr_native_unit_of_measurement = "%"

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
