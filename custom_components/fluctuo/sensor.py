"""Sensor platform for the Fluctuo integration."""
from __future__ import annotations

import base64
import logging
from datetime import timedelta, datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .fluctuo_api import FluctuoAPI

SCAN_INTERVAL = timedelta(minutes=5)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Fluctuo sensor from a config entry."""
    _LOGGER.debug("Setting up Fluctuo sensor")

    entry_data = hass.data["fluctuo"][config_entry.entry_id]
    api_key = entry_data["api_key"]
    providers = entry_data.get("providers", ["lime"])
    latitude = entry_data.get("latitude", hass.config.latitude)
    longitude = entry_data.get("longitude", hass.config.longitude)
    max_distance = entry_data.get("max_distance", 100)  # meters

    _LOGGER.debug(
        f"Fluctuo sensor configuration: providers={providers}, lat={latitude}, lon={longitude}, max_distance={max_distance}"
    )

    session = async_get_clientsession(hass)
    api = FluctuoAPI(session, api_key, providers, latitude, longitude)

    async_add_entities([FluctuoSensor(api, max_distance)], True)
    _LOGGER.debug("Fluctuo sensor added to Home Assistant")


class FluctuoSensor(SensorEntity):
    """Representation of a Fluctuo sensor."""

    def __init__(self, api: FluctuoAPI, max_distance: float):
        """Initialize the sensor."""
        self._api = api
        self._max_distance = max_distance
        self._state: StateType = None
        self._available = True
        self._attributes = {}
        self._nearby_vehicles = []
        _LOGGER.debug(f"Fluctuo sensor initialized with max_distance={max_distance}")

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Lime Scooters Available"

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"fluctuo_lime_{self._api.latitude}_{self._api.longitude}"

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "scooters"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:scooter-electric"

    def _decode_base64_id(self, encoded_id: str) -> str:
        """Decode the base64 ID and return the last part."""
        try:
            decoded = base64.b64decode(encoded_id).decode("utf-8")
            return decoded.split(":")[-1]
        except:
            return encoded_id  # Return original ID if decoding fails

    def _vehicle_to_dict(self, vehicle, distance: float):
        """Convert a vehicle object to a dictionary with decoded ID."""
        return {
            "id": self._decode_base64_id(vehicle.id),
            "public_id": vehicle.publicId,
            "battery": vehicle.battery,
            "distance": round(distance),
            "lat": vehicle.lat,
            "lng": vehicle.lng,
        }

    async def async_update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.debug("Updating Fluctuo sensor")
        try:
            vehicles = await self._api.get_vehicles()
            _LOGGER.debug(f"Retrieved {len(vehicles)} vehicles from Fluctuo API")
            self._nearby_vehicles = [
                v
                for v in vehicles
                if v.provider == "lime"
                and v.is_close_enough(
                    self._api.latitude, self._api.longitude, self._max_distance
                )
            ]
            self._state = len(self._nearby_vehicles)
            _LOGGER.debug(f"Found {self._state} nearby Lime scooters")

            self._attributes["last_update"] = datetime.now().isoformat()
            self._attributes["available_vehicles"] = [
                self._vehicle_to_dict(
                    v, v.distance_to(self._api.latitude, self._api.longitude)
                )
                for v in self._nearby_vehicles
            ]

            if self._state > 0:
                nearest_scooter = min(
                    self._nearby_vehicles,
                    key=lambda v: v.distance_to(
                        self._api.latitude, self._api.longitude
                    ),
                )
                self._attributes["nearest_scooter"] = self._vehicle_to_dict(
                    nearest_scooter,
                    nearest_scooter.distance_to(
                        self._api.latitude, self._api.longitude
                    ),
                )
            else:
                self._attributes["nearest_scooter"] = None

            self._available = True
        except Exception as error:
            _LOGGER.error(f"Error updating Fluctuo sensor: {error}")
            self._state = None
            self._attributes["last_update"] = datetime.now().isoformat()
            self._attributes["error"] = str(error)
            self._attributes["available_vehicles"] = []
            self._attributes["nearest_scooter"] = None
            self._available = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available
