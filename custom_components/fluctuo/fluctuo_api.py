import logging

import aiohttp
from gql import gql, Client
from geopy import distance as geopy_distance
from pydantic import BaseModel

from .aiohttp_existing_session import (
    AIOHTTPTransportExistingSession as AIOHTTPTransport,
)

_logger = logging.getLogger(__name__)

API_ENDPOINT = "https://flow-api.fluctuo.com/v1?access_token={api_key}"
VEHICLES_QUERY = """
    query GetVehicles($lat: Float!, $lng: Float!, $providers: [String!]) {
      vehicles(lat: $lat, lng: $lng, includeProviders: $providers, vehicleTypes: [SCOOTER]) {
        id,
        publicId,
        lat,
        lng,
        battery,
        provider {
            name
        }
      }
    }
"""


class Vehicle(BaseModel):
    id: str | None = None
    publicId: str | None = None
    lat: float | None = None
    lng: float | None = None
    battery: int | None = None
    provider: str | None = None

    def is_close_enough(self, lat, lng, distance):
        return (
            geopy_distance.distance((self.lat, self.lng), (lat, lng)).meters < distance
        )

    def distance_to(self, lat, lng):
        return geopy_distance.distance((self.lat, self.lng), (lat, lng)).meters

    def __str__(self):
        return f"Vehicle {self.id} ({self.publicId}) at {self.lat}, {self.lng} with {self.battery}% battery"

    def __repr__(self):
        return self.__str__()


class FluctuoAPI:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        providers: list[str],
        latitude: float,
        longitude: float,
    ):
        self.api_key = api_key
        self.providers = providers
        self.latitude = latitude
        self.longitude = longitude

        self._transport = AIOHTTPTransport(
            client_session=session, url=API_ENDPOINT.format(api_key=api_key)
        )

    async def _get_vehicles(self) -> list[Vehicle]:
        async with Client(
            transport=self._transport, fetch_schema_from_transport=True
        ) as session:
            query = gql(VEHICLES_QUERY)
            params = {
                "lat": self.latitude,
                "lng": self.longitude,
                "providers": self.providers,
            }
            response = await session.execute(query, variable_values=params)
            vehicles = []
            for vehicle in response["vehicles"]:
                vehicle["provider"] = vehicle["provider"]["name"].lower()
                vehicles.append(Vehicle(**vehicle))
            return vehicles

    async def get_vehicles(self) -> list[Vehicle]:
        try:
            return await self._get_vehicles()
        except Exception as err:
            _logger.error(f"An error occurred: {err}")
            return []
