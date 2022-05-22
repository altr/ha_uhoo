"""Support for Uhoo sensor."""

from pyuhoo.device import Device
from sqlalchemy import true

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import ATTRIBUTION, DOMAIN, SENSOR_TYPES


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Uhoo sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for serial_number in coordinator.data:
        device = coordinator.data.get(serial_number)
        for description in SENSOR_TYPES:
            sensors.append(UhooSensor(coordinator, device, description))

    async_add_entities(sensors, False)


class UhooSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Uhoo sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: Device,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the Uhoo sensor."""
        super().__init__(coordinator)

        self.device = device

        self._attr_name = "{0} {1}".format(device.name, description.device_class)
        self._attr_unique_id = "{}_{}".format(device.serial_number, description.name)
        self._attr_device_class = description.device_class
        self._attr_unit_of_measurement = description.native_unit_of_measurement
        self._attr_icon = description.icon
        self._type = description.name
        self.entity_description = description
        self.entity_id = f"{DOMAIN}.{device.name}_{description.device_class}"
        self._attr_entity_registry_visible_default = True

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.platform.config_entry.unique_id)},
            name=self.coordinator.name,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            getattr(self.device, self.entity_description.key) if self.device else None
        )
