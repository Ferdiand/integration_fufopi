# ADXL345 Python library for Raspberry Pi
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
#
# This is a Raspberry Pi Python implementation to help you get started with
# the Adafruit Triple Axis ADXL345 breakout board:
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

from decimal import Decimal
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    FREQUENCY_HERTZ,
    DEVICE_CLASS_FREQUENCY,
)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, DEVICE_CLASS_LOCK

from .const import DOMAIN, ATTRIBUTION


class HCM5883LEntity(CoordinatorEntity):
    """HCM5883L base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.address = 0x1E

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "HCM5883L"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "HCM5883L")},
            "name": "3-Axis Digital Compass IC",
            "model": "HMC5883L",
            "manufacturer": "Honeywell",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class HCM5883LSampleNoSensor(HCM5883LEntity, SensorEntity):
    """sample no sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Samples"

    @property
    def unique_id(self):
        return super().unique_id + "sampleno"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.i2c_hcm5883.sample_no)

        self.async_write_ha_state()


class HCM5883LOutputRateSensor(HCM5883LEntity, SensorEntity):
    """output rate sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Output rate"
        self._attr_device_class = DEVICE_CLASS_FREQUENCY
        self._attr_native_unit_of_measurement = FREQUENCY_HERTZ

    @property
    def unique_id(self):
        return super().unique_id + "output_rate"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.i2c_hcm5883.output_rate)

        self.async_write_ha_state()


class HCM5883LMeasureConfigSensor(HCM5883LEntity, SensorEntity):
    """meassure config sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Meas config"

    @property
    def unique_id(self):
        return super().unique_id + "meas_config"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.i2c_hcm5883.measurement_mode
        if val == 0:
            self._attr_native_value = "Normal"
        elif val == 1:
            self._attr_native_value = "Positive bias"
        elif val == 2:
            self._attr_native_value = "Negative bias"
        elif val == 3:
            self._attr_native_value = "Config reserved"
        else:
            self._attr_native_value = "Invalid"

        self.async_write_ha_state()


class HCM5883LRangeSensor(HCM5883LEntity, SensorEntity):
    """range sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Range"
        self._attr_native_unit_of_measurement = "Gauss"

    @property
    def unique_id(self):
        return super().unique_id + "range"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.i2c_hcm5883.sensor_range

        self.async_write_ha_state()


class HCM5883LGainSensor(HCM5883LEntity, SensorEntity):
    """gain sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Gain"
        self._attr_native_unit_of_measurement = "LSb/Gauss"

    @property
    def unique_id(self):
        return super().unique_id + "gain"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.i2c_hcm5883.gain

        self.async_write_ha_state()


class HCM5883LResolutionSensor(HCM5883LEntity, SensorEntity):
    """resolution sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Resolution"
        self._attr_native_unit_of_measurement = "mGauss/LSb"

    @property
    def unique_id(self):
        return super().unique_id + "resolution"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.i2c_hcm5883.resolution

        self.async_write_ha_state()


class HCM5883LOperationModeSensor(HCM5883LEntity, SensorEntity):
    """operation mode sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Operation mode"

    @property
    def unique_id(self):
        return super().unique_id + "op_mode"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.i2c_hcm5883.operating_mode
        if val == 0:
            self._attr_native_value = "Continuous-Measurement Mode"
        elif val == 1:
            self._attr_native_value = "Single-Measurement Mode"
        elif val == 2:
            self._attr_native_value = "Idle Mode"
        elif val == 3:
            self._attr_native_value = "Idle Mode"
        else:
            self._attr_native_value = "Invalid"

        self.async_write_ha_state()


class HCM5883Li2cHighSpeedBinarySensor(HCM5883LEntity, BinarySensorEntity):
    """HCM5883L i2c hight speed binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "i2c High Speed"

    @property
    def unique_id(self):
        return super().unique_id + "i2cHigh"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.i2c_hcm5883.i2c_high_speed

        self.async_write_ha_state()


class HCM5883LLockedBinarySensor(HCM5883LEntity, BinarySensorEntity):
    """HCM5883L locked binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Lock"
        self._attr_device_class = DEVICE_CLASS_LOCK

    @property
    def unique_id(self):
        return super().unique_id + "lock"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.i2c_hcm5883.is_locked

        self.async_write_ha_state()


class HCM5883LReadyBinarySensor(HCM5883LEntity, BinarySensorEntity):
    """HCM5883L ready binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Ready"

    @property
    def unique_id(self):
        return super().unique_id + "ready"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.i2c_hcm5883.is_ready

        self.async_write_ha_state()


class HCM5883LMagXSensor(HCM5883LEntity, SensorEntity):
    """mag x sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Mag X"
        self._attr_native_unit_of_measurement = "Gauss"
        self._attr_icon = "mdi:axis-x-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "magX"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            Decimal(self.coordinator.i2c_hcm5883.mag_x) * Decimal(0.001)
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class HCM5883LMagYSensor(HCM5883LEntity, SensorEntity):
    """mag y sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Mag Y"
        self._attr_native_unit_of_measurement = "Gauss"
        self._attr_icon = "mdi:axis-y-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "magY"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            Decimal(self.coordinator.i2c_hcm5883.mag_y) * Decimal(0.001)
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class HCM5883LMagZSensor(HCM5883LEntity, SensorEntity):
    """mag z sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Mag Z"
        self._attr_native_unit_of_measurement = "Gauss"
        self._attr_icon = "mdi:axis-z-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "magZ"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            Decimal(self.coordinator.i2c_hcm5883.mag_z) * Decimal(0.001)
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()
