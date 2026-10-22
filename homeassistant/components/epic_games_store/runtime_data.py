"""Runtime data for the Epic Games Store integration."""

from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .wish_list import EGSWishList


@dataclass
class EGSRuntimeData:
    """Data stored on the Epic Games Store config entry."""

    calendar: DataUpdateCoordinator[dict[str, list[dict[str, Any]]]]
    wishlist: DataUpdateCoordinator[list[dict[str, str]]]
    wish_list: EGSWishList


type EGSConfigEntry = ConfigEntry[EGSRuntimeData]
