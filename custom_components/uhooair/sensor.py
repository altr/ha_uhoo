"""Support for Uhoo sensor."""

from pyuhoo.device import Device

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
        self.entity_description = description
        self._uuid = device.serial_number
        self._device_class = description.device_class
        self._name = "{0} {1}".format(device.name, self._device_class)
        self._unit_of_measurement = description.unit_of_measurement
        self._type = description.name
        self._attr_icon = description.icon
        self._attr_unique_id = "{}_{}".format(self._uuid, self._type)

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
